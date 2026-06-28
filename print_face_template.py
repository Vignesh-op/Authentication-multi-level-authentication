#!/usr/bin/env python3
"""
Face Template Evaluation Tool
==============================
Prints and evaluates facial geometry templates stored in MongoDB.
Useful for debugging and understanding the face recognition system.
"""

import json
import sys
from pymongo import MongoClient
from pprint import pprint
from datetime import datetime
import base64
import cv2
import numpy as np

# MongoDB Configuration
MONGO_URI = 'mongodb://localhost:27017/authentication'

def connect_to_db():
    """Connect to MongoDB"""
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000, connectTimeoutMS=5000)
        # Test connection
        client.admin.command('ping')
        db = client['authentication']
        return db
    except Exception as e:
        print(f"❌ Error connecting to MongoDB: {e}")
        print("Make sure MongoDB is running on localhost:27017")
        print("  Command: mongod --dbpath .mongodb/data --logpath .mongodb/mongodb.log")
        return None

def print_all_face_templates():
    """Print all face templates in the database"""
    db = connect_to_db()
    if db is None:
        return
    
    users_collection = db['users']
    users = list(users_collection.find({}, {'facial_geometry': 1, 'email': 1, 'name': 1}))
    
    if not users:
        print("❌ No users found in database")
        return
    
    print("\n" + "="*80)
    print("FACIAL GEOMETRY TEMPLATES IN DATABASE")
    print("="*80)
    
    for i, user in enumerate(users, 1):
        print(f"\n📋 User {i}: {user.get('name', 'N/A')} ({user.get('email', 'N/A')})")
        print("-" * 80)
        
        geometry = user.get('facial_geometry')
        if not geometry:
            print("  ⚠️  No facial geometry stored for this user")
            continue
        
        # Print template metadata
        print(f"  Method:          {geometry.get('method', 'N/A')}")
        print(f"  Template Version: {geometry.get('template_version', 'N/A')}")
        
        # Print based on method
        if geometry.get('method') == 'dlib_68':
            print(f"  Landmarks:       {len(geometry.get('landmarks', []))} points")
            print(f"  Face Width:      {geometry.get('face_width', 'N/A'):.2f}")
            print(f"  Face Height:     {geometry.get('face_height', 'N/A'):.2f}")
            print(f"  Face Area:       {geometry.get('face_area', 'N/A'):.2f}")
            print(f"  Center:          ({geometry.get('face_center', [0, 0])[0]:.2f}, {geometry.get('face_center', [0, 0])[1]:.2f})")
            print(f"  Distances:       {len(geometry.get('inter_landmark_distances', []))} measurements")
            
            # Show first few landmarks
            landmarks = geometry.get('landmarks', [])
            if landmarks:
                print(f"\n  📍 First 5 Landmarks (normalized):")
                for j, lm in enumerate(landmarks[:5]):
                    print(f"     Landmark {j}: [{lm[0]:8.4f}, {lm[1]:8.4f}]")
                if len(landmarks) > 5:
                    print(f"     ... and {len(landmarks) - 5} more")
            
            # Show sample distances
            distances = geometry.get('inter_landmark_distances', [])
            if distances:
                print(f"\n  📏 Inter-landmark Distance Stats:")
                dist_arr = np.array(distances)
                print(f"     Min: {dist_arr.min():.4f}")
                print(f"     Max: {dist_arr.max():.4f}")
                print(f"     Mean: {dist_arr.mean():.4f}")
                print(f"     Std Dev: {dist_arr.std():.4f}")
        
        elif geometry.get('method') == 'cascade':
            print(f"  Face Box:        {geometry.get('face_box', 'N/A')}")
            print(f"  Face Width:      {geometry.get('face_width', 'N/A'):.2f}")
            print(f"  Face Height:     {geometry.get('face_height', 'N/A'):.2f}")
            print(f"  Face Area:       {geometry.get('face_area', 'N/A'):.2f}")
            print(f"  Aspect Ratio:    {geometry.get('aspect_ratio', 'N/A'):.4f}")
            print(f"  Center:          ({geometry.get('face_center', [0, 0])[0]:.2f}, {geometry.get('face_center', [0, 0])[1]:.2f})")
            print(f"  Eyes Detected:   {geometry.get('eye_count', 0)}")
            
            eyes = geometry.get('eyes', [])
            if eyes:
                print(f"\n  👁️  Eye Positions:")
                for j, eye in enumerate(eyes):
                    print(f"     Eye {j+1}: pos=({eye['x']:.1f}, {eye['y']:.1f}), size=({eye['width']:.1f}x{eye['height']:.1f})")
    
    print("\n" + "="*80)
    print(f"Total Users: {len(users)}")
    print("="*80 + "\n")

def print_specific_user(email):
    """Print template for a specific user"""
    db = connect_to_db()
    if db is None:
        return
    
    users_collection = db['users']
    user = users_collection.find_one({'email': email})
    
    if not user:
        print(f"❌ User with email '{email}' not found")
        return
    
    print("\n" + "="*80)
    print(f"FACIAL GEOMETRY TEMPLATE FOR: {user.get('name')} ({email})")
    print("="*80)
    
    geometry = user.get('facial_geometry')
    if not geometry:
        print("  ⚠️  No facial geometry stored for this user")
        return
    
    print("\n📊 Full Template Details:")
    print("-" * 80)
    pprint(geometry, width=80)
    print("="*80 + "\n")

def compare_templates(email1, email2):
    """Compare two facial geometry templates"""
    db = connect_to_db()
    if db is None:
        return
    
    users_collection = db['users']
    user1 = users_collection.find_one({'email': email1})
    user2 = users_collection.find_one({'email': email2})
    
    if not user1:
        print(f"❌ User with email '{email1}' not found")
        return
    if not user2:
        print(f"❌ User with email '{email2}' not found")
        return
    
    geom1 = user1.get('facial_geometry')
    geom2 = user2.get('facial_geometry')
    
    if not geom1 or not geom2:
        print("❌ One or both users have no facial geometry stored")
        return
    
    print("\n" + "="*80)
    print(f"COMPARING TEMPLATES")
    print(f"User 1: {user1.get('name')} ({email1})")
    print(f"User 2: {user2.get('name')} ({email2})")
    print("="*80)
    
    # Compare basic measurements
    print("\n📐 Measurement Comparison:")
    print(f"  Method 1:        {geom1.get('method')} vs {geom2.get('method')}")
    
    if geom1.get('method') == geom2.get('method'):
        if geom1.get('method') == 'cascade':
            w1 = geom1.get('face_width', 0)
            w2 = geom2.get('face_width', 0)
            h1 = geom1.get('face_height', 0)
            h2 = geom2.get('face_height', 0)
            
            print(f"  Face Width:      {w1:.2f} vs {w2:.2f} (diff: {abs(w1-w2):.2f})")
            print(f"  Face Height:     {h1:.2f} vs {h2:.2f} (diff: {abs(h1-h2):.2f})")
            print(f"  Aspect Ratio:    {geom1.get('aspect_ratio', 0):.4f} vs {geom2.get('aspect_ratio', 0):.4f}")
            print(f"  Eyes Detected:   {geom1.get('eye_count', 0)} vs {geom2.get('eye_count', 0)}")
    
    print("="*80 + "\n")

def print_template_statistics():
    """Print statistics about all face templates"""
    db = connect_to_db()
    if db is None:
        return
    
    users_collection = db['users']
    users = list(users_collection.find({}, {'facial_geometry': 1, 'email': 1}))
    
    if not users:
        print("❌ No users found in database")
        return
    
    methods = {}
    template_versions = {}
    with_geometry = 0
    without_geometry = 0
    
    for user in users:
        geometry = user.get('facial_geometry')
        if geometry:
            with_geometry += 1
            method = geometry.get('method', 'unknown')
            methods[method] = methods.get(method, 0) + 1
            
            version = geometry.get('template_version', 'unknown')
            template_versions[version] = template_versions.get(version, 0) + 1
        else:
            without_geometry += 1
    
    print("\n" + "="*80)
    print("FACIAL GEOMETRY TEMPLATES - STATISTICS")
    print("="*80)
    print(f"\nTotal Users:                 {len(users)}")
    print(f"Users with Geometry:         {with_geometry}")
    print(f"Users without Geometry:      {without_geometry}")
    print(f"\nMethod Distribution:")
    for method, count in methods.items():
        pct = (count / with_geometry * 100) if with_geometry > 0 else 0
        print(f"  {method:20s}: {count:3d} ({pct:5.1f}%)")
    print(f"\nTemplate Versions:")
    for version, count in template_versions.items():
        pct = (count / with_geometry * 100) if with_geometry > 0 else 0
        print(f"  Version {version:15s}: {count:3d} ({pct:5.1f}%)")
    print("="*80 + "\n")

def main():
    """Main menu"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'all':
            print_all_face_templates()
        elif command == 'stats':
            print_template_statistics()
        elif command == 'user' and len(sys.argv) > 2:
            print_specific_user(sys.argv[2])
        elif command == 'compare' and len(sys.argv) > 3:
            compare_templates(sys.argv[2], sys.argv[3])
        else:
            print_usage()
    else:
        print_usage()

def print_usage():
    """Print usage instructions"""
    print("\n" + "="*80)
    print("FACE TEMPLATE EVALUATION TOOL")
    print("="*80)
    print("\nUsage:")
    print("  python print_face_template.py all                    - Print all templates")
    print("  python print_face_template.py stats                  - Print statistics")
    print("  python print_face_template.py user <email>           - Print specific user template")
    print("  python print_face_template.py compare <email1> <email2> - Compare two templates")
    print("\nExamples:")
    print("  python print_face_template.py all")
    print("  python print_face_template.py stats")
    print("  python print_face_template.py user user@example.com")
    print("  python print_face_template.py compare user1@example.com user2@example.com")
    print("\n" + "="*80 + "\n")

if __name__ == '__main__':
    main()
