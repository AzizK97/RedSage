require 'json'
require 'base64'
require 'openssl'
require 'net/http'
require 'uri'

module AiChatWidgetHelper
  CACHE_TTL = 60
  ELIGIBILITY_TOKEN_TTL_SEC = 300
  HTTP_OPEN_TIMEOUT = Integer(ENV.fetch('REDSAGE_WIDGET_ELIGIBILITY_OPEN_TIMEOUT', '5'))
  HTTP_READ_TIMEOUT = Integer(ENV.fetch('REDSAGE_WIDGET_ELIGIBILITY_READ_TIMEOUT', '10'))

  # Returns a Hash of mount attributes if the user may see the widget, or nil.
  # Eligibility matches the API: provisioned on platform, role admin or project_manager, entitlement enabled.
  def ai_chat_widget_mount_data(user)
    return nil unless user&.logged?

    check = fetch_platform_widget_eligibility(user)
    unless truthy?(check['eligible'])
      # If dev_mode is enabled allow admins to mount the widget even when the
      # external eligibility check is missing/fails. This makes the plugin
      # usable immediately after installation for testing and initial setup.
      dev_mode = plugin_settings_hash['dev_mode']
      if truthy?(dev_mode) && user.admin?
        Rails.logger.warn('[redmine_ai_chat_widget] dev_mode enabled: mounting widget despite ineligible platform response')
      else
        log_mount_suppressed(user, check, 'eligible_false_or_missing')
        return nil
      end
    end

    role = check['platform_role'].to_s
    unless %w[admin project_manager].include?(role)
      log_mount_suppressed(user, check, "role_not_allowed:#{role.presence || 'blank'}")
      return nil
    end

    public_base = resolved_backend_url_public
    if public_base.empty?
      Rails.logger.warn(
        '[redmine_ai_chat_widget] mount suppressed: public/backend URL empty ' \
        '(set REDSAGE_BACKEND_PUBLIC_URL or plugin “Browser URL”, or internal URL via REDSAGE_BACKEND_URL)',
      )
      return nil
    end

    {
      user_id: user.id,
      user_login: user.login,
      user_role: role,
      widget_token: generate_widget_token(user),
      # Browser loads scripts and calls fetch() here; must resolve in the user’s browser (not host.docker.internal on Linux).
      backend_url: public_base
    }
  end

  def generate_widget_token(user)
    now = Time.now.to_i
    payload = {
      sub: user.id.to_s,
      redmine_user_id: user.id,
      login: user.login,
      email: user.mail,
      iat: now,
      exp: now + 3600
    }
    sign_plugin_jwt(payload)
  end

  private

  def truthy?(value)
    value == true || value.to_s == 'true'
  end

  def log_mount_suppressed(user, check, code)
    reason = check['_reason'].presence || check['reason'].presence || code
    detail = check['_detail'].presence || check['detail'].presence
    Rails.logger.info(
      "[redmine_ai_chat_widget] widget mount suppressed login=#{user.login} redmine_user_id=#{user.id} " \
      "reason=#{reason} detail=#{detail.inspect} " \
      '(Before RBAC the HTML mount rendered for every logged-in user; now it appears only when the platform ' \
      'returns eligible:true — check Redmine log above for HTTP/network/JWT lines.)'
    )
  end

  def plugin_settings_hash
    s = Setting.plugin_redmine_ai_chat_widget || {}
    defaults = Redmine::Plugin.find(:redmine_ai_chat_widget).settings[:default] || {}
    defaults.merge(s)
  end

  # URL the Redmine *server* uses for Net::HTTP (eligibility). Docker: host.docker.internal or service name.
  # REDSAGE_BACKEND_URL overrides plugin when set.
  def resolved_backend_url_internal
    env_url = ENV['REDSAGE_BACKEND_URL'].to_s.strip.sub(%r{/\z}, '')
    return env_url if env_url.present?

    plugin = plugin_settings_hash
    plugin['backend_url'].to_s.strip.sub(%r{/\z}, '').presence || ''
  end

  # URL embedded in HTML for the *browser* (script src, fetch base). Often https://api.company.com or http://localhost:8000.
  # REDSAGE_BACKEND_PUBLIC_URL overrides plugin when set; otherwise plugin “browser URL”; otherwise internal (same-origin-ish setups).
  def resolved_backend_url_public
    pub = ENV['REDSAGE_BACKEND_PUBLIC_URL'].to_s.strip.sub(%r{/\z}, '')
    return pub if pub.present?

    plugin = plugin_settings_hash
    default_settings = Redmine::Plugin.find(:redmine_ai_chat_widget).settings[:default] || {}
    p = plugin['backend_url_public'].to_s.strip.sub(%r{/\z}, '')
    p = default_settings['backend_url_public'].to_s.strip.sub(%r{/\z}, '') if p.empty?
    return p if p.present?

    resolved_backend_url_internal
  end

  def resolved_jwt_secret
    plugin = plugin_settings_hash
    default_settings = Redmine::Plugin.find(:redmine_ai_chat_widget).settings[:default] || {}
    s = plugin['jwt_secret'].to_s.strip
    s = default_settings['jwt_secret'].to_s.strip if s.empty?
    s.presence || ENV['REDSAGE_JWT_SECRET'].to_s.strip
  end

  def resolved_jwt_issuer
    plugin = plugin_settings_hash
    default_settings = Redmine::Plugin.find(:redmine_ai_chat_widget).settings[:default] || {}
    plugin['jwt_issuer'].to_s.strip.presence ||
      default_settings['jwt_issuer'].to_s.strip.presence ||
      ENV['REDSAGE_JWT_ISSUER'].to_s.strip
  end

  def resolved_jwt_audience
    plugin = plugin_settings_hash
    default_settings = Redmine::Plugin.find(:redmine_ai_chat_widget).settings[:default] || {}
    plugin['jwt_audience'].to_s.strip.presence ||
      default_settings['jwt_audience'].to_s.strip.presence ||
      ENV['REDSAGE_JWT_AUDIENCE'].to_s.strip
  end

  # Server-to-server token: same JWT secret as user tokens (no extra gate secret).
  def generate_eligibility_token(user)
    now = Time.now.to_i
    payload = {
      sub: 'redmine_plugin',
      purpose: 'widget_eligibility',
      target_redmine_user_id: user.id,
      iat: now,
      exp: now + ELIGIBILITY_TOKEN_TTL_SEC
    }
    sign_plugin_jwt(payload)
  end

  def sign_plugin_jwt(payload)
    header = { typ: 'JWT', alg: 'HS256' }

    issuer = resolved_jwt_issuer
    audience = resolved_jwt_audience

    payload = payload.dup
    payload[:iss] = issuer unless issuer.empty?
    payload[:aud] = audience unless audience.empty?

    secret = resolved_jwt_secret
    return nil if secret.empty?

    header_b64 = urlsafe_b64encode(JSON.generate(header))
    payload_b64 = urlsafe_b64encode(JSON.generate(payload))

    signing_input = "#{header_b64}.#{payload_b64}"
    signature = OpenSSL::HMAC.digest('sha256', secret, signing_input)
    signature_b64 = urlsafe_b64encode(signature)

    "#{signing_input}.#{signature_b64}"
  end

  def fetch_platform_widget_eligibility(user)
    jwt_secret = resolved_jwt_secret
    backend_url = resolved_backend_url_internal

    return { 'eligible' => false, '_reason' => 'missing_jwt_secret' } if jwt_secret.empty?
    return { 'eligible' => false, '_reason' => 'missing_backend_url' } if backend_url.empty?

    cache_key = "ai_chat_widget_eligibility:#{user.id}"
    Rails.cache.fetch(cache_key, expires_in: CACHE_TTL) do
      request_widget_eligibility_http(backend_url, user)
    end
  end

  def request_widget_eligibility_http(backend_url, user)
    token = generate_eligibility_token(user)
    if token.blank?
      Rails.logger.warn('[redmine_ai_chat_widget] eligibility skipped: jwt_secret not configured')
      return { 'eligible' => false, '_reason' => 'token_sign_failed' }
    end

    uri = URI.parse("#{backend_url}/api/internal/widget-eligibility?redmine_user_id=#{user.id.to_i}")
    http = Net::HTTP.new(uri.host, uri.port)
    http.use_ssl = (uri.scheme == 'https')
    http.open_timeout = HTTP_OPEN_TIMEOUT
    http.read_timeout = HTTP_READ_TIMEOUT

    req = Net::HTTP::Get.new(uri.request_uri)
    req['Authorization'] = "Bearer #{token}"
    req['Accept'] = 'application/json'

    response = http.request(req)
    body = response.body.to_s
    unless response.code == '200'
      msg = "[redmine_ai_chat_widget] eligibility HTTP #{response.code} from #{backend_url}#{uri.path}: #{body.truncate(300)}"
      Rails.logger.warn(msg)
      if response.code == '401'
        Rails.logger.warn(
          '[redmine_ai_chat_widget] 401 usually means JWT_SECRET in Redmine does not match JWT_SECRET on the API ' \
          '(copy from backend .env; watch for typos: e.g. mlxhdbz vs mlxHdbz, Bw5XNk vs BwSXNk).'
        )
      end
      return {
        'eligible' => false,
        '_reason' => "http_#{response.code}",
        '_detail' => body.truncate(500)
      }
    end

    parsed = JSON.parse(body)
    if parsed.is_a?(Hash) && !truthy?(parsed['eligible'])
      Rails.logger.info(
        "[redmine_ai_chat_widget] platform denied widget (eligible:false) for redmine_user_id=#{user.id} — " \
        'not provisioned, role not admin/pm, or entitlement disabled in redsage DB.'
      )
    end
    parsed
  rescue StandardError => e
    Rails.logger.warn("[redmine_ai_chat_widget] eligibility check failed: #{e.class}: #{e.message}")
    {
      'eligible' => false,
      '_reason' => 'network_or_parse_error',
      '_detail' => e.message.to_s.truncate(300)
    }
  end

  def urlsafe_b64encode(str)
    Base64.urlsafe_encode64(str).delete('=')
  end
end
