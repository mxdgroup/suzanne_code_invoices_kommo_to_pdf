#!/usr/bin/env python3
"""
MongoDB Helper for Invoice Management
Handles database operations for proforma invoices
"""
import os
import logging
from typing import Optional, Dict, Any
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from datetime import datetime

logger = logging.getLogger(__name__)

class MongoDBHelper:
    """Helper class for MongoDB operations"""
    
    def __init__(self):
        """Initialize MongoDB connection"""
        self.client = None
        self.db = None
        self.collection = None
        self._connect()
    
    def _connect(self):
        """Establish connection to MongoDB"""
        try:
            # Get MongoDB connection string from environment
            mongo_url = os.getenv("MONGO_URL")
            
            if not mongo_url:
                # Fallback: construct from individual components
                mongo_host = os.getenv("MONGOHOST", "localhost")
                mongo_port = os.getenv("MONGOPORT", "27017")
                mongo_user = os.getenv("MONGOUSER", "")
                mongo_password = os.getenv("MONGOPASSWORD", "")
                
                if mongo_user and mongo_password:
                    mongo_url = f"mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}"
                else:
                    mongo_url = f"mongodb://{mongo_host}:{mongo_port}"
            
            logger.info(f"🔌 Connecting to MongoDB...")
            self.client = MongoClient(
                mongo_url,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000
            )
            
            # Test connection
            self.client.admin.command('ping')
            
            # Select database and collection
            self.db = self.client['invoices_db']
            self.collection = self.db['proforma_invoices']
            
            logger.info("✓ Connected to MongoDB successfully")
            
        except ConnectionFailure as e:
            logger.error(f"❌ Failed to connect to MongoDB: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"❌ MongoDB connection error: {str(e)}")
            raise
    
    def find_by_deal_number(self, deal_number: str) -> Optional[Dict[str, Any]]:
        """
        Find a proforma invoice by deal number
        
        Args:
            deal_number: The deal number to search for
            
        Returns:
            Invoice document if found, None otherwise
        """
        try:
            if self.collection is None:
                raise Exception("MongoDB collection not initialized")
            
            document = self.collection.find_one({"deal_number": deal_number})
            
            if document:
                logger.info(f"✓ Found existing invoice for deal number: {deal_number}")
            else:
                logger.info(f"ℹ No existing invoice found for deal number: {deal_number}")
            
            return document
            
        except OperationFailure as e:
            logger.error(f"❌ MongoDB query error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"❌ Error finding invoice: {str(e)}")
            raise
    
    def insert_invoice(self, invoice_data: Dict[str, Any]) -> str:
        """
        Insert a new proforma invoice
        
        Args:
            invoice_data: The invoice data to insert
            
        Returns:
            The inserted document ID
        """
        try:
            if self.collection is None:
                raise Exception("MongoDB collection not initialized")
            
            # Create a copy to avoid modifying the original dict
            data_to_insert = invoice_data.copy()
            
            # Add metadata
            data_to_insert['created_at'] = datetime.utcnow()
            data_to_insert['updated_at'] = datetime.utcnow()
            
            result = self.collection.insert_one(data_to_insert)
            
            logger.info(f"✓ Inserted new invoice with ID: {result.inserted_id}")
            return str(result.inserted_id)
            
        except OperationFailure as e:
            logger.error(f"❌ MongoDB insert error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"❌ Error inserting invoice: {str(e)}")
            raise
    
    def update_invoice(self, deal_number: str, invoice_data: Dict[str, Any]) -> bool:
        """
        Update an existing proforma invoice by deal number
        
        Args:
            deal_number: The deal number to update
            invoice_data: The new invoice data
            
        Returns:
            True if update was successful
        """
        try:
            if self.collection is None:
                raise Exception("MongoDB collection not initialized")
            
            # Create a copy to avoid modifying the original dict
            data_to_update = invoice_data.copy()
            
            # Add updated timestamp
            data_to_update['updated_at'] = datetime.utcnow()
            
            # Remove _id if present (can't update _id field)
            data_to_update.pop('_id', None)
            data_to_update.pop('created_at', None)  # Don't update created_at
            
            result = self.collection.update_one(
                {"deal_number": deal_number},
                {"$set": data_to_update}
            )
            
            if result.modified_count > 0:
                logger.info(f"✓ Updated invoice for deal number: {deal_number}")
                return True
            else:
                logger.warning(f"⚠ No changes made to invoice for deal number: {deal_number}")
                return True  # Document exists but no changes needed
                
        except OperationFailure as e:
            logger.error(f"❌ MongoDB update error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"❌ Error updating invoice: {str(e)}")
            raise
    
    def upsert_invoice(self, deal_number: str, invoice_data: Dict[str, Any]) -> tuple[bool, str]:
        """
        Insert or update a proforma invoice based on deal number
        
        Args:
            deal_number: The deal number
            invoice_data: The invoice data
            
        Returns:
            Tuple of (is_new, document_id/message)
        """
        try:
            existing = self.find_by_deal_number(deal_number)
            
            if existing:
                # Update existing
                self.update_invoice(deal_number, invoice_data)
                return (False, str(existing['_id']))
            else:
                # Insert new
                doc_id = self.insert_invoice(invoice_data)
                return (True, doc_id)
                
        except Exception as e:
            logger.error(f"❌ Error in upsert operation: {str(e)}")
            raise
    
    def close(self):
        """Close MongoDB connection"""
        if self.client is not None:
            self.client.close()
            logger.info("✓ MongoDB connection closed")


# Singleton instance
_db_helper = None

def get_db_helper() -> MongoDBHelper:
    """Get or create MongoDB helper instance"""
    global _db_helper
    if _db_helper is None:
        _db_helper = MongoDBHelper()
    return _db_helper

