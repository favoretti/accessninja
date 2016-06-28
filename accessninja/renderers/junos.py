class JunosRenderer(object):
    def __init__(self, device):
        self._device = device

    def render(self):
        self.render_junos_hostgroups()
        self.render_junos_rules()
        self.render_config()

    def render_junos_rules(self):
        for ruleset in self._device.rules:
            self.render_junos_icmp_rules(ruleset.name, ruleset.icmp_rules)
            self.render_junos_tcp_rules(ruleset.name, ruleset.tcp_rules)

    def render_config(self):
        rendered_config = ''
        if len(self._device.rendered_groups):
            rendered_config = '\n'.join(self._device.rendered_groups)

        for ruleset_name, rules in self._device.rendered_rules.iteritems():
            ruleset_name += '-v4'
            rendered_config += '\ndelete firewall filter {}'.format(ruleset_name)
            for idx, rule in enumerate(rules):
                rendered_config += '\nedit firewall filter {} term {}'.format(ruleset_name, idx + 1)
                rendered_config += '\n' + rule
                rendered_config += '\ntop'
            rendered_config += '\nset firewall filter {} term DROP_ALL then syslog'.format(ruleset_name)
            rendered_config += '\nset firewall filter {} term DROP_ALL then discard\n'.format(ruleset_name)

        self._device.rendered_config = rendered_config

    def render_junos_icmp_rules(self, name, icmp_rules):
        for rule in icmp_rules:
            if name not in self._device.rendered_rules:
                self._device.rendered_rules[name] = list()
            self._device.rendered_rules[name].append(rule.render_junos())

    def render_junos_tcp_rules(self, name, tcp_rules):
        for rule in tcp_rules:
            if name not in self._device.rendered_rules:
                self._device.rendered_rules[name] = list()
            self._device.rendered_rules[name].append(rule.render_junos(self._device.portgroups))

    def render_junos_hostgroups(self):
        for hg in self._device.hostgroups:
            self._device.rendered_groups.append(hg.render_junos())
