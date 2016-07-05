class IOSRenderer(object):
    def __init__(self, device):
        self._device = device

    def render(self):
        self.render_ios_hostgroups()
        self.render_ios_portgroups()
        self.render_ios_rules()
        self.render_config()

    def render_ios_rules(self):
        for ruleset in self._device.rules:
            #self.render_junos_icmp_rules(ruleset.name, ruleset.icmp_rules)
            self.render_ios_tcp_rules(ruleset.name, ruleset.tcp_rules)

    def render_config(self):
        rendered_config = ''
        if len(self._device.rendered_groups):
            rendered_config = '\n'.join(self._device.rendered_groups)

        for ruleset_name, rules in self._device.rendered_rules.iteritems():
            ruleset_name += '-v4'
            rendered_config += '\nno ip access-list extended {}'.format(ruleset_name)
            rendered_config += '\nip access-list extended {}'.format(ruleset_name)
            for idx, rule in enumerate(rules):
                rendered_config += '\n' + rule

            rendered_config += '\nexit'

        self._device.rendered_config = rendered_config

    def render_ios_icmp_rules(self, name, icmp_rules):
        for rule in icmp_rules:
            if name not in self._device.rendered_rules:
                self._device.rendered_rules[name] = list()
            self._device.rendered_rules[name].append(rule.render_junos())

    def render_ios_tcp_rules(self, name, tcp_rules):
        for rule in tcp_rules:
            if name not in self._device.rendered_rules:
                self._device.rendered_rules[name] = list()
            self._device.rendered_rules[name].append(rule.render_ios())

    def render_ios_hostgroups(self):
        for hg in self._device.hostgroups:
            self._device.rendered_groups.append(hg.render_ios())

    def render_ios_portgroups(self):
        for pg in self._device.portgroups:
            self._device.rendered_groups.append(pg.render_ios())

