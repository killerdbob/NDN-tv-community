from ndn.app import NDNApp
from ndn.app_support.nfd_mgmt import ControlParameters, ControlParametersValue, parse_response, Strategy
from ndn.utils import timestamp, gen_nonce_64
from ndn.encoding import Component, SignatureInfo, TypeNumber, Name, get_tl_num_size, write_tl_num, NonStrictName
from ndn.security import DigestSha256Signer
from ndn.name_tree import PrefixTreeNode
import struct
import logging
import asyncio as aio
from typing import Optional, Awaitable, Coroutine
from ndn.types import Validator, Route, InterestNack, InterestTimeout, InterestCanceled, ValidationFailure


def make_command(module, command, **kwargs):
    ret = Name.from_str(f"/localhop/nfd/{module}/{command}")

    # Command parameters
    cp = ControlParameters()
    cp.cp = ControlParametersValue()
    for k, v in kwargs.items():
        if k == 'strategy':
            cp.cp.strategy = Strategy()
            cp.cp.strategy.name = v
        else:
            setattr(cp.cp, k, v)
    ret.append(Component.from_bytes(cp.encode()))

    # Timestamp and nonce
    ret.append(Component.from_bytes(struct.pack('!Q', timestamp())))
    ret.append(Component.from_bytes(struct.pack('!Q', gen_nonce_64())))

    # SignatureInfo
    signer = DigestSha256Signer()
    sig_info = SignatureInfo()
    signer.write_signature_info(sig_info)
    buf = sig_info.encode()
    ret.append(Component.from_bytes(bytes([TypeNumber.SIGNATURE_INFO, len(buf)]) + buf))

    # SignatureValue
    sig_size = signer.get_signature_value_size()
    tlv_length = 1 + get_tl_num_size(sig_size) + sig_size
    buf = bytearray(tlv_length)
    buf[0] = TypeNumber.SIGNATURE_VALUE
    offset = 1 + write_tl_num(sig_size, buf, 1)
    signer.write_signature_value(memoryview(buf)[offset:], ret)
    ret.append(Component.from_bytes(buf))

    return ret


class NDNRemoteApp(NDNApp):

    async def main_loop(self, after_start: Awaitable = None) -> bool:
        """
        The main loop of NDNApp.

        :param after_start: the coroutine to start after connection to NFD is established.
        :return: ``True`` if the connection is shutdown not by ``Ctrl+C``.
            For example, manually or by the other side.
        """
        self._prefix_register_semaphore = aio.Semaphore(1)

        async def starting_task():
            for name, route, validator, need_raw_packet, need_sig_ptrs in self._autoreg_routes:
                success = await self.register(name, route, validator, need_raw_packet, need_sig_ptrs)
                if not success:
                    exit(0)
            if after_start:
                try:
                    await after_start
                except Exception:
                    self.face.shutdown()
                    raise

        try:
            await self.face.open()
        except (FileNotFoundError, ConnectionError, OSError, PermissionError):
            if after_start:
                if isinstance(after_start, Coroutine):
                    after_start.close()
                elif isinstance(after_start, (aio.Task, aio.Future)):
                    after_start.cancel()
            raise
        task = aio.create_task(starting_task())
        logging.debug('Connected to NFD node, start running...')
        try:
            await self.face.run()
            ret = True
        except aio.CancelledError:
            logging.info('Shutting down')
            ret = False
        finally:
            self.face.shutdown()
        self._clean_up()
        await task
        return ret 

    async def register(self, name: NonStrictName, func: Optional[Route], validator: Optional[Validator] = None,
                       need_raw_packet: bool = False, need_sig_ptrs: bool = False) -> bool:
        """
        Register a route for a specific prefix dynamically.

        :param name: the Name prefix for this route.
        :type name: :any:`NonStrictName`
        :param func: the onInterest function for the specified route.
            If ``None``, the NDNApp will only send the register command to forwarder,
            without setting any callback function.
        :type func: Optional[Callable[[:any:`FormalName`, :any:`InterestParam`, Optional[:any:`BinaryStr`]], ``None``]]
        :param validator: the Validator used to validate coming Interests.
        :type validator: Optional[:any:`Validator`]
        :return: ``True`` if the registration succeeded.
        :param need_raw_packet: if True, pass the raw Interest packet to the callback as a keyword argument
            ``raw_packet``.
        :type need_raw_packet: bool
        :param need_sig_ptrs: if True, pass the Signature pointers to the callback as a keyword argument
            ``sig_ptrs``.
        :type need_sig_ptrs: bool

        :raises ValueError: the prefix is already registered.
        :raises NetworkError: the face to NFD is down now.
        """
        name = Name.normalize(name)
        if func is not None:
            node = self._prefix_tree.setdefault(name, PrefixTreeNode())
            if node.callback:
                raise ValueError(f'Duplicated registration: {Name.to_str(name)}')
            node.callback = func
            node.extra_param = {'raw_packet': need_raw_packet, 'sig_ptrs': need_sig_ptrs}
            if validator:
                node.validator = validator

        # Fix the issue that NFD only allows one packet signed by a specific key for a timestamp number
        async with self._prefix_register_semaphore:
            try:
                _, _, reply = await self.express_interest(make_command('rib', 'register', name=name), lifetime=1000)
                ret = parse_response(reply)
                if ret['status_code'] != 200:
                    logging.error(f'Registration for {Name.to_str(name)} failed: '
                                  f'{ret["status_code"]} {bytes(ret["status_text"]).decode()}')
                    return False
                else:
                    logging.debug(f'Registration for {Name.to_str(name)} succeeded: '
                                  f'{ret["status_code"]} {bytes(ret["status_text"]).decode()}')
                    return True
            except (InterestNack, InterestTimeout, InterestCanceled, ValidationFailure) as e:
                logging.error(f'Registration for {Name.to_str(name)} failed: {e.__class__.__name__}')
                return False

    async def unregister(self, name: NonStrictName) -> bool:
        """
        Unregister a route for a specific prefix.

        :param name: the Name prefix.
        :type name: :any:`NonStrictName`
        """
        name = Name.normalize(name)
        del self._prefix_tree[name]
        try:
            await self.express_interest(make_command('rib', 'unregister', name=name), lifetime=1000)
            return True
        except (InterestNack, InterestTimeout, InterestCanceled, ValidationFailure):
            return False
