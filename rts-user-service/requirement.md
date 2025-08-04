# User Service Requirements
{
    "_id": ObjectId("..."),
    "email": "user@example.com",
    "username": "john_doe",
    "subscriptionStatus": "pro",
    "roles": ["standard", "pro"],
    
    
    "profile": {
    "firstName": "John",
    "lastName": "Doe",
    "avatar": "https://cdn.example.com/avatars/123.jpg",
    
        // Personal user
        "dateOfBirth": "1990-05-15",
        "interests": ["tech", "travel"],
        
        // Business user (different fields)
        "companyName": "ABC Corp",
        "taxId": "123456789",
        "businessType": "software"
    },
    

    "preferences": {
        "language": "vi",
        "timezone": "Asia/Ho_Chi_Minh",
        "notifications": {
            "email": true,
            "push": false,
            "marketing": true
        },
        "privacy": {
            "profileVisibility": "public",
            "showEmail": false
        }
    },
    
    "createdAt": ISODate("2024-01-01"),
    "lastLogin": ISODate("2024-08-04")
}