from wgconfig import WGConfig


class WG(WGConfig):

    def add_peer(self, key, leading_comment=None):
        """Adds a new peer with the given (public) key"""
        if key in self.peers:
            raise KeyError('Peer to be added already exists')
        self.lines.append('') # append an empty line for separation
        # self.handle_leading_comment(leading_comment) # add leading comment if needed
        # Append peer with key attribute
        self.lines.append(f'[Peer] {leading_comment}')
        self.lines.append('{0} = {1}'.format(self.keyattr, key))
        # Invalidate data cache
        self.invalidate_data()
