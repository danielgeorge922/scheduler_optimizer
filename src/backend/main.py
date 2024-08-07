from auth import create_token, verify_token

def main():
    # Generate a token
    user_id = 'user1'
    token = create_token(user_id)
    token = 'fjwdjf'
    print(f"Generated Token: {token}")

    # Verify the token
    verified_user = verify_token(token)
    if verified_user:
        print(f"Verified User ID: {verified_user}")
    else:
        print("Invalid or expired token")

if __name__ == '__main__':
    main()
