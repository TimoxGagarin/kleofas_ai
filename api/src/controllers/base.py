from uuid import UUID

from fastapi import APIRouter, Depends, Query, UploadFile, status

from api.src.controllers.users import get_current_superuser
from api.src.dao.base import BaseDAO
from api.src.exceptions import EntityDoesntExist
from api.src.schemas.users import DisplayUser
from api.src.utils.utils import process_csv_file, process_json_file, remove_none_values


class BaseRouter(APIRouter):
    def __init__(
        self,
        entity_name,
        entity_dao: BaseDAO,
        display_entity,
        search_entity=None,
        create_entity=None,
        update_entity=None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.entity_name = entity_name
        self.entity_dao = entity_dao
        self.create_entity = create_entity
        self.update_entity = update_entity
        self.display_entity = display_entity
        self.search_entity = search_entity

        self.pk_type = int if str(self.entity_dao.model.id.type) == "BIGINT" else UUID
        [
            getattr(self, el)(
                summary=(
                    f"{' '.join(el[8:].split('_'))} {self.entity_name}"
                ).capitalize()
            )
            for el in dir(self)
            if el.startswith("entity__")
        ]

    def entity__get_all(self, summary):
        if self.search_entity is None:
            return

        @self.get("", summary=summary)
        async def router(
            data: self.search_entity = Query(),
        ) -> list[self.display_entity]:
            return await self.entity_dao.find_all(
                **remove_none_values(data.model_dump())
            )

    def entity__get_by_id(self, summary):
        @self.get("/{entity_id}", summary=summary)
        async def router(
            entity_id: self.pk_type,
        ) -> self.display_entity:
            existed_topic = await self.entity_dao.find_by_id(entity_id)
            if not existed_topic:
                raise EntityDoesntExist(self.entity_name)
            return existed_topic

    def entity__create(self, summary):
        if self.create_entity is None:
            return

        @self.post("", status_code=status.HTTP_201_CREATED, summary=summary)
        async def router(
            data: self.create_entity, user: DisplayUser = Depends(get_current_superuser)
        ) -> self.display_entity:
            return await self.entity_dao.add(**data.dict())

    def entity__import_csv(self, summary):
        if self.create_entity is None:
            return

        @self.post("/import/csv", status_code=status.HTTP_201_CREATED, summary=summary)
        async def router(
            file: UploadFile, user: DisplayUser = Depends(get_current_superuser)
        ) -> list[self.display_entity]:
            return await process_csv_file(file, self.create_entity, self.entity_dao)

    def entity__import_json(self, summary):
        if self.create_entity is None:
            return

        @self.post("/import/json", status_code=status.HTTP_201_CREATED, summary=summary)
        async def router(
            file: UploadFile, user: DisplayUser = Depends(get_current_superuser)
        ) -> list[self.display_entity]:
            return await process_json_file(file, self.create_entity, self.entity_dao)

    def entity__update(self, summary):
        if self.update_entity is None:
            return

        @self.patch("/{entity_id}", summary=summary)
        async def router(
            entity_id: self.pk_type,
            data: self.update_entity,
            user: DisplayUser = Depends(get_current_superuser),
        ) -> self.display_entity:
            topic = await self.entity_dao.find_by_id(entity_id)
            if not topic:
                raise EntityDoesntExist(self.entity_name)
            return await self.entity_dao.update(entity_id, **data.dict())

    def entity__delete(self, summary):
        @self.delete(
            "/{entity_id}", status_code=status.HTTP_204_NO_CONTENT, summary=summary
        )
        async def router(
            entity_id: self.pk_type, user: DisplayUser = Depends(get_current_superuser)
        ):
            await self.entity_dao.delete(id=entity_id)
