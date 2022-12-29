from pymongo import MongoClient, errors

from config import data
from utils import DBCollections


class ApiMongoDB:
	def __init__(self):
		self.project = 'WoWsItaliaBot'
		self.db_name = "WoWsItalia"
		try:
			self.client = MongoClient(serverSelectionTimeoutMS=10)
			self.client = MongoClient(f"mongodb+srv://{data['MONGO_USER']}:{data['MONGO_PASSWORD']}@cluster0.rtvit"
                                      f".mongodb.net/{self.project}?retryWrites=true&w=majority")
		except (errors.ConnectionFailure, errors.ServerSelectionTimeoutError):
			raise Exception("Database non connesso")

    ####################################################################################################################
    #                                                   PRIVATE API                                                    #
    ####################################################################################################################
    # Parametric API to mongo
	def __get_element(self, collection: DBCollections, query: dict) -> dict:
		"""
		Gets an element which matches with `query` from a collection of the database.
		Args:
			collection: The collection of the database.
			query: The query.
		Returns:
			A dictionary represents the result of the function `find_one`.
			 If an error occurs, it returns an empty dictionary.
		"""
		try:
			return self.client[self.db_name][str(collection)].find_one(query)
		except Exception as error:
			print(f"Error: Mongo __get_element({str(DBCollections)}, {query})\n{error}")
			return {}
	
	def __insert_element(self, collection: DBCollections, document: dict) -> dict:
		"""
		Inserts an element in a collection of the database.
		Args:
			collection: The collection of the database.
			document: The data to insert.
		Returns:
			The inserted document.
			 If an error occurs or if the document is not inserted, it returns an empty dictionary.
		"""
		try:
			insertedDocument = self.client[self.db_name][str(collection)].insert_one(document)
			document["_id"] = insertedDocument.inserted_id
			return document
		except errors.DuplicateKeyError:
			print(f"Error: Mongo __insert_element({str(DBCollections)}, {document})\nDuplicated Key")
		except errors.WriteError as error:
			if error.code == 121:
				print(f"Error: Mongo __insert_element({str(DBCollections)}, {document})\nInvalid schema")
			else:
				print(f"Error: Mongo __insert_element({str(DBCollections)}, {document})\n{error}")
		except Exception as error:
			print(f"Error: Mongo __insert_element({str(DBCollections)}, {document})\n{error}")
		return {}
	
	####################################################################################################################
	#                                                    PUBLIC API                                                    #
	####################################################################################################################
	
	####################################################################################################################
	#                                              Player Collection API                                               #
	####################################################################################################################
	def search_player(self, discord_id: str = "", wows_id: str = "") -> dict:
		"""
		Returns the player's data that Discord's id and WoWs' id matches with `discord_id` or `wows_id`.
		Args:
			discord_id: the Discord's id.
			wows_id: the WoWs' id.
		Returns:
			The player data.
			 If the player is not found or if an error occurs, it returns an empty dictionary.
		"""
		return self.__get_element(
			DBCollections.PLAYERS,
			{"$or": [{"discord": discord_id}, {"wows": wows_id}]}
		)
	
	def insert_player(self, discord_id: str, wows_id: str, token: str = "", expire: str = "") -> dict:
		"""
		Inserts a player in the collection.
		Args:
			discord_id: The Discord's id of the player.
			wows_id: The WoWs' id of the player.
			token: The token to access the personal data of the wargaming API.
			expire: The date of the token's expire.
		Returns:
			The inserted player.
			 If an error occurs, it returns an empty dictionary.
		"""
		return self.__insert_element(
			DBCollections.PLAYERS,
			{
				"discord": discord_id,
				"wows": wows_id,
				"token": token,
				"expire": expire
			}
		)
