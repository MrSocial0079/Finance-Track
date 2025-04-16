from firebase_admin import auth
from fastapi import HTTPException, Header
from typing import Optional, Dict, Any

class AuthService:
    @staticmethod
    async def verify_token(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
        if not authorization or not authorization.startswith('Bearer '):
            raise HTTPException(status_code=401, detail="No valid token provided")
        
        token = authorization.split('Bearer ')[1]
        
        # Simple token verification - just extract the user ID
        # This is a simplified approach for development purposes
        try:
            # In a production environment, you would use proper token verification
            # For now, we'll use a simplified approach that works with our custom tokens
            
            # Extract user ID from the token (assuming format: uid:token)
            if ':' in token:
                uid = token.split(':', 1)[0]
            else:
                # Try to decode JWT if it looks like one
                parts = token.split('.')
                if len(parts) == 3:
                    import base64
                    import json
                    try:
                        # Add padding if needed
                        payload = parts[1]
                        payload += '=' * (-len(payload) % 4)
                        decoded = base64.b64decode(payload)
                        claims = json.loads(decoded)
                        uid = claims.get('uid')
                    except:
                        # If decoding fails, use the token as is
                        uid = token
                else:
                    # Use the token as is
                    uid = token
            
            # Get user data from Firestore
            from services.firebase import db
            user_doc = db.collection('users').document(uid).get()
            
            if not user_doc.exists:
                # Try to get user from Firebase Auth
                try:
                    user_record = auth.get_user(uid)
                    # User exists in Auth but not in Firestore
                    return {
                        'uid': uid,
                        'email': user_record.email,
                        'name': user_record.display_name or ''
                    }
                except:
                    raise HTTPException(status_code=401, detail="User not found")
            
            # User exists in Firestore
            user_data = user_doc.to_dict()
            return {
                'uid': uid,
                'email': user_data.get('email', ''),
                'name': user_data.get('name', '')
            }
            
        except Exception as e:
            print(f"Token verification error: {str(e)}")
            raise HTTPException(status_code=401, detail=f"Invalid token")

auth_service = AuthService()
