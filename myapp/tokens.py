from django.contrib.auth.tokens import PasswordResetTokenGenerator 

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    # This class generates tokens for account activation.
    #it inherits from djangos PasswordResetTokenGenerator class, which is designed to create secure, time-sensitive tokens.
    def _make_hash_value(self, user, timestamp):
        # This method creates a unique hash value for the user and timestamp.
        #constructs a single string by concatenating several pieces of information:
        #text_type is used to ensure compatibility with both Python 2 and 3. and it converts the user primary key, timestamp, and active state to strings.
        #This string is then used to generate a hash that serves as the token.
        return(
            str(user.pk)+ #ensures the token is tied to specific user.
            str(timestamp)+ #provided by parent class, used to ensure the token is time-sensitive.(defauts to 3 days if not set)
            str(user.is_active) #crucial for security, ensuring the token is unique to the user's active state
        )
    
account_activation_token=AccountActivationTokenGenerator()
# This instance of AccountActivationTokenGenerator can be used to generate and verify account activation tokens.
# It overrides the _make_hash_value method to include the user's primary key, timestamp, and active state in the token generation process.    

#Django already has a robust mechanism for generating tokens, primarily used for its password reset functionality. This PasswordResetTokenGenerator class is designed to create secure, time-sensitive tokens.
#Instead of reinventing the wheel, we leverage this existing, well-tested Django class as a base for our account activation tokens.
