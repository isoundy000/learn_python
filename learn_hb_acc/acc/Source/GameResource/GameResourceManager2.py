#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import os

from sqlalchemy.orm.exc import NoResultFound

from Source.Log.Write import Log
from Source.DataBase.Common.DBEngine import DBEngine
from Source.DataBase.Table.t_section_resource import t_section_resource
from Source.DataBase.Table.t_section_resource_files import t_section_resource_files
from Source.Config.ConfigManager import ConfigManager


class GameResourceManager:

    # static members define
    _resource_dict = {}
    _max = {}

    # static functions define
    @staticmethod
    def Data():
        return GameResourceManager._resource_dict

    @staticmethod
    def Init():
        session = DBEngine.NewSession()
        try:
            resourceVersions = session.query(t_section_resource).\
                filter(t_section_resource.status == "excute").\
                order_by(t_section_resource.id.desc()).all()

            if resourceVersions is None:
                Log.Write("[Error]GameResource Error: No GameResource Excute")
                return False

            appConfig = ConfigManager.Singleton()

            GameResourceManager._resource_dict = {}

            for resourceVersion in resourceVersions:
                version = resourceVersion.id
                needrestart = resourceVersion.needrestart
                versionFiles = session.query(t_section_resource_files).filter(t_section_resource_files.r_id == version).all()

                if versionFiles is None:
                    continue

                versionFilesData = []

                for versionFile in versionFiles:
                    versionFileData = {
                        "version": version,
                        "id": versionFile.id,
                        "url": versionFile.url,
                        "filepath": versionFile.filepath,
                        "platform": versionFile.platform,
                        "length": versionFile.length,
                        "needrestart": needrestart,
                        "url2": versionFile.url2,
                        "url3": versionFile.url3,
                    }
                    versionFilesData.append(versionFileData)

                GameResourceManager._resource_dict[version] = versionFilesData
                # Log.Write("GameResourceManager", GameResourceManager._resource_dict)
            return True
        except NoResultFound, nf:
            Log.Write("[Error]Database Error: %s" % str(nf))
            return False
        finally:
            DBEngine.DelSession(session)

    @staticmethod
    def UpdateVersion(version):
        session = DBEngine.NewSession()
        try:
            versionFilesData = []
            targetVersion = session.query(t_section_resource).filter(t_section_resource.id == version).\
                filter(t_section_resource.status == "excute").first()
            if targetVersion:
                appConfig = ConfigManager.Singleton()
                # GameResourceManager._resource_dict = {}
                needrestart = targetVersion.needrestart
                versionFiles = session.query(t_section_resource_files). \
                    filter(t_section_resource_files.r_id == version).all()
                if versionFiles:
                    for versionFile in versionFiles:
                        versionFileData = {
                            "version": version,
                            "id": versionFile.id,
                            "url": versionFile.url,
                            "filepath": versionFile.filepath,
                            "platform": versionFile.platform,
                            "length": versionFile.length,
                            "needrestart": needrestart,
                            "url2": versionFile.url2,
                            "url3": versionFile.url3,
                        }
                        versionFilesData.append(versionFileData)
            if not versionFilesData:
                if GameResourceManager._resource_dict.has_key(version):
                    del GameResourceManager._resource_dict[version]
            else:
                GameResourceManager._resource_dict[version] = versionFilesData
            # Log.Write("GameResourceManager", GameResourceManager._resource_dict)
            return True
        except NoResultFound, nf:
            Log.Write("[Error]Database Error: %s" % str(nf))
            return False
        finally:
            DBEngine.DelSession(session)