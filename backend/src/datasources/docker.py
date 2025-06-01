import docker
from docker.errors import APIError
from typing import Optional


class DockerDatasource:
    def __init__(self) -> None:
        self.client = docker.from_env()

    def list_containers(self, search: str = "") -> list:
        containers = self.client.containers.list(all=True)
        result = []
        for c in containers:
            try:
                networks = list(c.attrs["NetworkSettings"]["Networks"].keys())
            except KeyError:
                networks = []
            try:
                volumes_list = []
                mounts = c.attrs.get("Mounts", [])
                for m in mounts:
                    # если том именованный, m["Name"], иначе — путь назначения
                    volumes_list.append(m.get("Name") or m.get("Destination") or "")
            except KeyError:
                volumes_list = []
            result.append(
                {
                    "id": c.id,
                    "name": c.name,
                    "status": c.status,
                    "image": c.image.tags[0] if c.image.tags else "",
                    "networks": ", ".join(networks),
                    "volumes": volumes_list,
                }
            )
        return [r for r in result if search.lower() in r["name"].lower()]

    def remove_container(self, container_id: str) -> str:
        container = self.client.containers.get(container_id=container_id)
        container.remove(force=True)
        return container_id

    def start_container(self, container_id: str) -> None:
        container = self.client.containers.get(container_id=container_id)
        if container.status != "running":
            container.start()

    def stop_container(self, container_id: str) -> None:
        container = self.client.containers.get(container_id=container_id)
        if container.status == "running":
            container.stop()

    def get_logs(
        self,
        container_id: str,
        since: Optional[int] = None,
        until: Optional[int] = None,
    ) -> str:
        container = self.client.containers.get(container_id=container_id)
        kwargs = {"stdout": True, "stderr": True, "timestamps": False}
        if since is not None:
            kwargs["since"] = since
        if until is not None:
            kwargs["until"] = until
        try:
            logs_bytes = container.logs(**kwargs)
            if isinstance(logs_bytes, bytes):
                return logs_bytes.decode(errors="ignore")
            else:
                # Если возвращается генератор
                decoded = b"".join(logs_bytes)
                return decoded.decode(errors="ignore")
        except APIError as e:
            raise

    def exec_command(self, container_id: str, cmd: str) -> str:
        container = self.client.containers.get(container_id=container_id)
        result = container.exec_run(cmd)
        return result.output.decode(errors="ignore")


docker_datasource = DockerDatasource()
