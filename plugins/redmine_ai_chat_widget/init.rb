require_dependency File.expand_path('../lib/redmine_ai_chat_widget/hooks', __FILE__)
require_dependency File.expand_path('../app/helpers/ai_chat_widget_helper', __FILE__)

# Mix the helper into all views
ActionView::Base.include AiChatWidgetHelper

Redmine::Plugin.register :redmine_ai_chat_widget do
  name 'Redmine AI Chat Widget'
  author 'Aziz'
  description 'Floating AI chatbot widget for Redmine'
  version '0.1.0'
  url 'https://github.com/AzizK97/Redmine-Agent'
  author_url 'https://github.com/AzizK97'
  settings default: {
    # Server-side (Net::HTTP from Redmine). Docker: override with REDSAGE_BACKEND_URL=http://host.docker.internal:8000
    'backend_url' => 'http://localhost:8000',
    # Browser (script src / fetch). Dev Docker: set REDSAGE_BACKEND_PUBLIC_URL=http://localhost:8000 or fill below.
    'backend_url_public' => '',
    'jwt_secret' => '66uwKYHYwBmlxhdbzEv+ixJcwhZqi/osB/PwyBw5XNk=',
    'jwt_issuer' => 'redsage',
    'jwt_audience' => 'redsage-web',
    # When true, allows admins to mount the widget even if the external
    # backend eligibility check fails or is unreachable. Useful for first-time
    # installs and development. Disable in production if you want strict gating.
    'dev_mode' => true
  }, partial: 'settings/redmine_ai_chat_widget_settings'
end
