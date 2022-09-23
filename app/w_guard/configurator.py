import wgconfig
import subprocess
import ipaddress


class WGConfigurator:

    def __init__(self, pub_key, name):
        self.pub_key = pub_key
        self.name = name

    def get_configuration(self):
        wc = wgconfig.WGConfig('wg0')
        wc.read_file()
        return wc

    def get_new_ip(self, _conf):
        used_ips = []
        for i, v in _conf.peers.items():
            try:
                used_ips.append(ipaddress.ip_address(v['AllowedIPs'].replace("/32", "")))
            except ValueError:
                continue
        return str(sorted(used_ips)[-1] + 1) + "/32"

    def add_new_peer(self, _conf):
        new_ip = self.get_new_ip(_conf)
        try:
            _conf.add_peer(self.pub_key, f'#{self.name}')
        except KeyError:
            return _conf.peers[self.pub_key]["AllowedIPs"]
        _conf.add_attr(self.pub_key, 'AllowedIPs', new_ip)
        subprocess.call(['sudo', 'chmod', '756', '/etc/wireguard/wg0.conf'])
        _conf.write_file()
        subprocess.call(['sudo', 'chmod', '755', '/etc/wireguard/wg0.conf'])
        return new_ip

    def restart_wg(self):
        subprocess.call(['sudo', 'wg-quick', 'down', '/etc/wireguard/wg0.conf'])
        subprocess.call(['sudo', 'wg-quick', 'up', '/etc/wireguard/wg0.conf'])

    def del_old_peer(self, key):
        _conf = self.get_configuration()
        _conf.del_peer(key)
        subprocess.call(['sudo', 'chmod', '756', '/etc/wireguard/wg0.conf'])
        _conf.write_file()
        subprocess.call(['sudo', 'chmod', '755', '/etc/wireguard/wg0.conf'])

    def update_configuration(self):
        conf = self.get_configuration()
        _ip = self.add_new_peer(conf)
        self.restart_wg()
        return _ip
