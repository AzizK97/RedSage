require 'json'
require 'base64'
require 'openssl'

module AiChatWidgetHelper
  def generate_widget_token(user)
    # Generate a simple JWT-like token using OpenSSL (no external gem needed)
    # Format: base64(header).base64(payload).hmac_signature
    
    header = { typ: 'JWT', alg: 'HS256' }
    settings = Setting.plugin_redmine_ai_chat_widget || {}
    default_settings = Redmine::Plugin.find(:redmine_ai_chat_widget).settings[:default] || {}

    payload = {
      sub: user.id.to_s,
      redmine_user_id: user.id,
      login: user.login,
      email: user.mail,
      iat: Time.now.to_i,
      exp: (Time.now + 1.hour).to_i
    }

    issuer = settings['jwt_issuer'].to_s.strip
    issuer = default_settings['jwt_issuer'].to_s.strip if issuer.empty?

    audience = settings['jwt_audience'].to_s.strip
    audience = default_settings['jwt_audience'].to_s.strip if audience.empty?

    payload[:iss] = issuer unless issuer.empty?
    payload[:aud] = audience unless audience.empty?

    secret = settings['jwt_secret'].to_s.strip
    secret = default_settings['jwt_secret'].to_s.strip if secret.empty?
    
    # Encode header and payload as base64url
    header_b64 = urlsafe_b64encode(JSON.generate(header))
    payload_b64 = urlsafe_b64encode(JSON.generate(payload))
    
    # Create signature
    signing_input = "#{header_b64}.#{payload_b64}"
    signature = OpenSSL::HMAC.digest('sha256', secret, signing_input)
    signature_b64 = urlsafe_b64encode(signature)
    
    # Return complete token
    "#{signing_input}.#{signature_b64}"
  end
  
  private
  
  def urlsafe_b64encode(str)
    Base64.urlsafe_encode64(str).delete('=')
  end
end
