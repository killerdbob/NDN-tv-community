from config import *
from ndn.encoding import Name, Component

from utils.oss_crud import NDNMinio
from utils.ndn_remote_app import NDNRemoteApp
# from utils.udp_face import default_face
from ndn.client_conf import default_face
from ndn.app import NDNApp

import logging
logging.basicConfig(format='[{asctime}]{levelname}:{message}',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG,
                    style='{')


def main():
    @app.route(arg_prefix + '/record')
    def on_interest(int_name, _int_param, _app_param):
        print('*' * 100)
        prefix = Name.to_str(int_name)
        print('get interest ' + prefix)
        data = {}
        if prefix.endswith('.m3u8'):
            # if Component.get_type(int_name[-1]) != Component.TYPE_SEGMENT:
            print("serve 1")
            data = oss_inst.fast_get_segment(
                Name.to_str(int_name) + '.ndn', VERSION, '0')

        else:
            # if Component.get_type(int_name[-1]) == Component.TYPE_SEGMENT:
            print("serve 2")
            segment_number = str(Component.to_number(int_name[-1]))
            version = VERSION
            if Component.get_type(int_name[-2]) == Component.TYPE_VERSION:
                version = Component.to_number(int_name[-2])
            raw_prefix = Name.to_str(int_name[:-2])
            data = oss_inst.fast_get_segment(
                raw_prefix + '.ndn', version, segment_number)
        if not data:
            return
        packet = data.get('packet')
        app.put_raw_packet(packet)


if __name__ == '__main__':
    arg_prefix = PREFIX
    arg_version = VERSION

    try:
        oss_inst = NDNMinio(host=OSS_HOST + ":" + str(OSS_PORT),
                            user=OSS_USER,
                            password=OSS_PASSWORD,
                            bucket=OSS_BUCKET)
    except Exception as e:
        print(e)

    app = NDNRemoteApp(face=default_face(REGISTER_NODE))
    main()
    try:
        app.run_forever()
    except Exception as e:
        print(e)
        exit(-1)
