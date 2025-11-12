"""
Database Manager Module - Fixed for Python 3.11 SSL Issues
Handles all MongoDB operations with SSL/TLS workaround
"""

import uuid
import certifi
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
from config import (
    MONGO_URI,
    MONGO_CONNECTION_PARAMS,
    DATABASE_NAME,
    COLLECTION_JD,
    COLLECTION_RESUMES,
    COLLECTION_RESULTS,
    COLLECTION_RUBRICS
)


class DatabaseManager:
    def __init__(self):
        """Initialize MongoDB connection with Python 3.11 SSL fix"""
        try:
            print("=" * 60)
            print("🔄 Attempting MongoDB Atlas connection...")
            print("=" * 60)

            # Connect using parameters from config.py
            self.client = MongoClient(MONGO_URI, **MONGO_CONNECTION_PARAMS)

            # Test connection immediately
            self.client.admin.command('ping')
            print("✅ MongoDB connection established successfully!")
            print(f"📦 Connected to database: {DATABASE_NAME}")

            self.db = self.client[DATABASE_NAME]

            self.jd_collection = self.db[COLLECTION_JD]
            self.resumes_collection = self.db[COLLECTION_RESUMES]
            self.results_collection = self.db[COLLECTION_RESULTS]
            self.rubrics_collection = self.db[COLLECTION_RUBRICS]

            print("📊 Collections initialized:")
            print(f"   • {COLLECTION_JD}")
            print(f"   • {COLLECTION_RESUMES}")
            print(f"   • {COLLECTION_RESULTS}")
            print(f"   • {COLLECTION_RUBRICS}")

            self._create_indexes()
            print("=" * 60)

        except ServerSelectionTimeoutError as e:
            print("=" * 60)
            print("❌ MONGODB CONNECTION TIMEOUT ERROR")
            print("=" * 60)
            error_str = str(e)
            if "SSL" in error_str or "TLS" in error_str:
                print("🔍 SSL/TLS Handshake Issue Detected")
            print(f"\n📋 Error Details: {error_str[:300]}...\n")

            print("💡 TROUBLESHOOTING CHECKLIST:")
            print("   1. ✅ Check your internet connection")
            print("   2. ✅ Verify MongoDB Atlas IP whitelist:")
            print("      → Go to Network Access in Atlas")
            print("      → Add 0.0.0.0/0 for testing")
            print("   3. ✅ Verify credentials in .env file")
            print("   4. ✅ Check MongoDB cluster is running")
            print("   5. ✅ Try Python 3.9 or 3.10 if issue persists")
            print("   6. ✅ Check corporate firewall/VPN")
            print("=" * 60)
            raise Exception("MongoDB connection failed. See troubleshooting steps above.")

        except ConnectionFailure as e:
            print("=" * 60)
            print("❌ MONGODB CONNECTION FAILURE")
            print("=" * 60)
            print(f"Error: {str(e)[:300]}")
            print("\n💡 This usually means:")
            print("   • Wrong username or password")
            print("   • Database user doesn't have permissions")
            print("   • Connection string is malformed")
            print("=" * 60)
            raise

        except Exception as e:
            print("=" * 60)
            print(f"❌ UNEXPECTED ERROR: {type(e).__name__}")
            print("=" * 60)
            print(f"Details: {str(e)[:300]}")
            print("=" * 60)
            raise

    def _create_indexes(self):
        """Create database indexes for better performance"""
        try:
            self.jd_collection.create_index("jd_id", unique=True)
            self.resumes_collection.create_index("resume_id", unique=True)
            self.results_collection.create_index([("jd_id", 1), ("resume_id", 1)])
            self.rubrics_collection.create_index("jd_id", unique=True)
            print("✅ Database indexes created successfully")
        except Exception as e:
            print(f"⚠️  Index creation warning (non-critical): {str(e)[:100]}")

    # ============== JD Operations ==============

    def save_jd(self, jd_data, filename):
        """Save parsed JD to database"""
        jd_id = "JD_" + str(uuid.uuid4())[:8].upper()

        jd_document = {
            'jd_id': jd_id,
            'filename': filename,
            'timestamp': datetime.now().isoformat(),
            **jd_data
        }

        self.jd_collection.insert_one(jd_document)
        print(f"💾 JD saved: {jd_id}")
        return jd_id

    def get_jd(self, jd_id):
        """Get JD by ID"""
        return self.jd_collection.find_one({'jd_id': jd_id}, {'_id': 0})

    def get_all_jds(self):
        """Get all JDs"""
        return list(self.jd_collection.find({}, {'_id': 0}).sort('timestamp', -1))

    def get_recent_jds(self, limit=5):
        """Get recent JDs"""
        return list(self.jd_collection.find({}, {'_id': 0}).sort('timestamp', -1).limit(limit))

    def count_all_jds(self):
        """Count total JDs"""
        return self.jd_collection.count_documents({})

    def delete_jd(self, jd_id):
        """Delete JD and all associated data"""
        self.jd_collection.delete_one({'jd_id': jd_id})
        self.results_collection.delete_many({'jd_id': jd_id})
        self.rubrics_collection.delete_one({'jd_id': jd_id})
        print(f"🗑️  JD deleted: {jd_id}")

    # ============== Rubrics Operations ==============

    def save_rubrics(self, jd_id, rubrics_data):
        """Save rubrics configuration for a JD"""
        rubrics_document = {
            'jd_id': jd_id,
            'timestamp': datetime.now().isoformat(),
            **rubrics_data
        }

        self.rubrics_collection.update_one(
            {'jd_id': jd_id},
            {'$set': rubrics_document},
            upsert=True
        )

        print(f"💾 Rubrics saved for: {jd_id}")
        return True

    def get_rubrics(self, jd_id):
        """Get rubrics configuration for a JD"""
        return self.rubrics_collection.find_one({'jd_id': jd_id}, {'_id': 0})

    def delete_rubrics(self, jd_id):
        """Delete rubrics for a JD"""
        self.rubrics_collection.delete_one({'jd_id': jd_id})

    # ============== Resume Operations ==============

    def save_resume(self, resume_data, filename):
        """Save parsed resume to database"""
        resume_id = "RES_" + str(uuid.uuid4())[:8].upper()

        resume_document = {
            'resume_id': resume_id,
            'filename': filename,
            'timestamp': datetime.now().isoformat(),
            **resume_data
        }

        self.resumes_collection.insert_one(resume_document)
        print(f"💾 Resume saved: {resume_id}")
        return resume_id

    def get_resume(self, resume_id):
        """Get resume by ID"""
        return self.resumes_collection.find_one({'resume_id': resume_id}, {'_id': 0})

    def get_all_resumes(self):
        """Get all resumes"""
        return list(self.resumes_collection.find({}, {'_id': 0}).sort('timestamp', -1))

    def get_recent_resumes(self, limit=5):
        """Get recent resumes"""
        return list(self.resumes_collection.find({}, {'_id': 0}).sort('timestamp', -1).limit(limit))

    def count_all_resumes(self):
        """Count total resumes"""
        return self.resumes_collection.count_documents({})

    def delete_resume(self, resume_id):
        """Delete a resume"""
        self.resumes_collection.delete_one({'resume_id': resume_id})
        self.results_collection.delete_many({'resume_id': resume_id})
        print(f"🗑️  Resume deleted: {resume_id}")

    # ============== Evaluation Results Operations ==============

    def save_evaluation_results(self, results_list):
        """Save evaluation results"""
        if not results_list:
            return 0

        for result in results_list:
            result['result_id'] = "RESULT_" + str(uuid.uuid4())[:8].upper()
            result['timestamp'] = datetime.now().isoformat()

        self.results_collection.insert_many(results_list)
        print(f"💾 Saved {len(results_list)} evaluation results")
        return len(results_list)

    def get_results_for_jd(self, jd_id):
        """Get all evaluation results for a JD, sorted by rank"""
        return list(self.results_collection.find(
            {'jd_id': jd_id},
            {'_id': 0}
        ).sort('rank', 1))

    def get_results_for_resume(self, resume_id):
        """Get all evaluation results for a specific resume"""
        return list(self.results_collection.find(
            {'resume_id': resume_id},
            {'_id': 0}
        ).sort('overall_score', -1))

    def get_top_candidates(self, jd_id, limit=10):
        """Get top N candidates for a JD"""
        return list(self.results_collection.find(
            {'jd_id': jd_id},
            {'_id': 0}
        ).sort('rank', 1).limit(limit))

    def get_recent_results(self, limit=5):
        """Get recent evaluation results"""
        return list(self.results_collection.find(
            {},
            {'_id': 0}
        ).sort('timestamp', -1).limit(limit))

    def count_all_results(self):
        """Count total evaluation results"""
        return self.results_collection.count_documents({})

    def clear_results_for_jd(self, jd_id):
        """Clear previous evaluation results for a JD"""
        deleted = self.results_collection.delete_many({'jd_id': jd_id})
        print(f"🗑️  Cleared {deleted.deleted_count} previous results for {jd_id}")

    def delete_result(self, result_id):
        """Delete a specific result"""
        self.results_collection.delete_one({'result_id': result_id})

    # ============== Statistics & Analytics ==============

    def get_jd_statistics(self, jd_id):
        """Get comprehensive statistics for a JD"""
        results = self.get_results_for_jd(jd_id)

        stats = {
            'total_candidates': len(results),
            'jd_id': jd_id
        }

        if results:
            scores = [r.get('overall_score', 0) for r in results]
            stats['average_score'] = round(sum(scores) / len(scores), 2)
            stats['highest_score'] = max(scores)
            stats['lowest_score'] = min(scores)

            tiers = {'HIGH': 0, 'MODERATE': 0, 'LOW': 0}
            for result in results:
                tier = result.get('candidate_tier', 'MODERATE')
                tiers[tier] = tiers.get(tier, 0) + 1

            stats['tier_distribution'] = tiers
            stats['high_tier_candidates'] = tiers['HIGH']
            stats['moderate_tier_candidates'] = tiers['MODERATE']
            stats['low_tier_candidates'] = tiers['LOW']
        else:
            stats['average_score'] = 0
            stats['highest_score'] = 0
            stats['lowest_score'] = 0
            stats['tier_distribution'] = {'HIGH': 0, 'MODERATE': 0, 'LOW': 0}
            stats['high_tier_candidates'] = 0
            stats['moderate_tier_candidates'] = 0
            stats['low_tier_candidates'] = 0

        return stats

    def get_resume_statistics(self, resume_id):
        """Get statistics for a specific resume across all JDs"""
        results = self.get_results_for_resume(resume_id)

        stats = {
            'total_applications': len(results),
            'resume_id': resume_id
        }

        if results:
            scores = [r.get('overall_score', 0) for r in results]
            stats['average_score'] = round(sum(scores) / len(scores), 2)
            stats['highest_score'] = max(scores)
            stats['best_match_jd'] = max(results, key=lambda x: x.get('overall_score', 0)).get('jd_id')
        else:
            stats['average_score'] = 0
            stats['highest_score'] = 0
            stats['best_match_jd'] = None

        return stats

    def get_global_statistics(self):
        """Get global system statistics"""
        return {
            'total_jds': self.count_all_jds(),
            'total_resumes': self.count_all_resumes(),
            'total_evaluations': self.count_all_results(),
            'total_rubrics': self.rubrics_collection.count_documents({})
        }

    def close(self):
        """Close MongoDB connection"""
        self.client.close()
        print("🔌 MongoDB connection closed")