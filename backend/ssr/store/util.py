from ssr.store import STATUS


class StateModule:
    name = None

    def update_module_status(self):
        STATUS.update(self.name, self.get_module_status())


def action(f):
    f.isAction = True
    return f
