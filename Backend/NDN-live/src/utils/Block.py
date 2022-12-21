from ndn.app import NDNApp
from ndn.encoding.name import *
from ndn.utils import timestamp
from config import *

from status import *
from utils.udp_face import default_face

from base64 import b64decode, b64encode
from ndn.app_support.security_v2 import parse_certificate, sign_req
from ndn.client_conf import read_client_conf, default_keychain

def singleton(clsObject):
    def inner(*args, **kwargs):
        if not hasattr(clsObject, "ins"):
            insObject = clsObject(*args, **kwargs)
            setattr(clsObject, "ins", insObject)
        return getattr(clsObject, "ins")
    return inner


@singleton
class BlockCrypto():
    def __init__(self, keyLocator=PREFIX, loadPath='/root/.ndn'):
        self.config = read_client_conf()
        self.keychain = default_keychain(self.config['pib'], self.config['tpm'])

        # self.privkey = ''
        # self.tpm_file = self.config['tpm'].split(':')[1]
        # with open(self.tpm_file,'r') as f:
        #     self.privkey = f.read()
        # self.pubkey = None
        # self.keychain = KeychainSqlite3(loadPath+os.sep+'pib.db', TpmFile(tpm_file))
        self.certPEM = b64encode(self.keychain[keyLocator].default_key().default_cert().data)
        self.cert_data = parse_certificate(self.keychain[keyLocator].default_key().default_cert().data)
        self.cert_name = self.cert_data.name
        self.signer = self.keychain.get_signer({'cert': self.cert_name})
        # self.signer = Sha256WithEcdsaSigner(self.certDER.name, b64decode(self.privkey))

class Block:
    def __init__(self):
        self.app = NDNApp(face=default_face())

    def make_data(self, prefix='', version=VERSION, metadata=b'', freshness_period=RECORD_FRESHNESS_PERIOD,
                  current_block=0, final_block_id=0, status=LIVE, time_stamp=0):
        name = Name.normalize(prefix)
        if version:
            name.append(Component.from_version(version))
        else:
            name.append(Component.from_version(timestamp()))
        name.append(Component.from_segment(current_block))
        packet = b''

        # metadata = base64.b64encode(metadata)
        bc = BlockCrypto()
        for _ in range(10):
            try:
                packet = self.app.prepare_data( Name.to_str(name), 
                                                metadata,
                                                freshness_period=freshness_period,
                                                final_block_id=Component.from_segment(final_block_id),
                                                signer=bc.signer)
                break
            except Exception as e:
                print(e)
                print('retry prepare_data')

        tmp_data = dict()
        tmp_data['prefix'] = Name.to_str(name)
        tmp_data['segment_number'] = str(current_block)
        # tmp_data['metadata'] = metadata
        tmp_data['freshness_period'] = freshness_period
        tmp_data['final_block_id'] = final_block_id
        tmp_data['time_stamp'] = time_stamp
        tmp_data['status'] = status
        tmp_data['packet'] = bytes(packet)
        return tmp_data
