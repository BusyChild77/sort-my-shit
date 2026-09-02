from inspect import signature

from pysman.service_manager import ServiceManager

from src.application.view.SMSView import SMSView


class ViewManager:
    """Instantiates the views with their dependencies and keeps the live instances.

    Views are mounted into a container, and remounted whenever the interface has to
    be rebuilt, for instance after a theme change.
    """

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(ViewManager, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.view_container = {}
        self.view_blueprints = {}
        self.container = None

    def set_service_manager(self, service_manager: ServiceManager):
        self.service_manager = service_manager

    def set_views(self, views: dict[str, SMSView]):
        self.view_blueprints = views

    def get(self, view_name: str) -> SMSView:
        return self.view_container[view_name]

    def mount(self, container):
        self.unmount()
        self.container = container

        for view_name, view in self.view_blueprints.items():
            self.view_container[view_name] = self.__instantiate(container, view)

    def unmount(self):
        for view in self.view_container.values():
            view.destroy()

        self.view_container = {}

    def __instantiate(self, container, view: SMSView) -> SMSView:
        dependencies = signature(view).parameters

        view_dependencies = [container]
        for dependency_name in dependencies:
            if dependency_name == "container":
                continue

            annotation = dependencies[dependency_name].annotation
            view_dependencies.append(self.service_manager.get_service(annotation.__name__))

        return view(*view_dependencies)
