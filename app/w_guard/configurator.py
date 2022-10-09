import ipaddress
import subprocess
from wgconfig import WGConfig


class WG(WGConfig):

    def add_peer(self, key, leading_comment=None):
        """Adds a new peer with the given (public) key and name"""
        if key in self.peers:
            raise KeyError('Peer to be added already exists')
        self.lines.append('')
        self.lines.append(f'[Peer] # {leading_comment}')
        self.lines.append('{0} = {1}'.format(self.keyattr, key))
        # Invalidate data cache
        self.invalidate_data()


class WGConfigurator:

    def __init__(self, name=None, pub_key=""):
        self.pub_key = pub_key
        self.name = name

    def get_configuration(self):
        wc = WG('wg0')
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
            _conf.add_peer(self.pub_key, leading_comment=self.name)
        except KeyError:
            return _conf.peers[self.pub_key]["AllowedIPs"]
        _conf.add_attr(self.pub_key, 'AllowedIPs', new_ip)
        self.save_configuration(_conf)
        return new_ip

    def restart_wg(self):
        subprocess.call(['sudo', 'wg-quick', 'down', '/etc/wireguard/wg0.conf'])
        subprocess.call(['sudo', 'wg-quick', 'up', '/etc/wireguard/wg0.conf'])

    def save_configuration(self, _conf):
        subprocess.call(['sudo', 'chmod', '756', '/etc/wireguard/wg0.conf'])
        _conf.write_file()
        subprocess.call(['sudo', 'chmod', '755', '/etc/wireguard/wg0.conf'])

    def del_old_peer(self):
        _conf = self.get_configuration()
        try:
            _conf.del_peer(self.pub_key)
            message = f"{self.name}  --- Was deleted"
            self.save_configuration(_conf)
            self.restart_wg()
        except KeyError:
            return f"No {self.name} in wg0.conf"
        return message

    def get_peers(self):
        peers = {}
        _conf = self.get_configuration()
        for peer in _conf.peers.values():
            try:
                peers[peer["PublicKey"]] = peer["_rawdata"][0].split("#")[1]
            except IndexError:
                peers[peer["PublicKey"]] = peer["_rawdata"][0]
        return peers

    def update_configuration(self):
        conf = self.get_configuration()
        _ip = self.add_new_peer(conf)
        self.restart_wg()
        return _ip
