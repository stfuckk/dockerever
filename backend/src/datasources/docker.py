import docker


class DockerDatasource:
    def __init__(self) -> None:
        self.client = docker.from_env()

    def list_containers(self, search: str = "") -> list:
        containers = self.client.containers.list(all=True)
        return [
            {
                "id": c.id,
                "name": c.name,
                "status": c.status,
                "image": c.image.tags[0] if c.image.tags else "",
            }
            for c in containers
            if search.lower() in c.name.lower()
        ]

    def remove_container(self, container_id: str) -> str:
        container = self.client.containers.get(container_id=container_id)
        container.remove(force=True)
        return container_id

    def get_logs(self, container_id: str) -> str:
        container = self.client.containers.get(container_id=container_id)
        return container.logs().decode()

    def exec_command(self, container_id: str, cmd: str) -> str:
        container = self.client.containers.get(container_id=container_id)
        return container.exec_run(cmd).output.decode()


docker_datasource = DockerDatasource()
