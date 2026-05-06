module RedmineAiChatWidget
  class Hooks < Redmine::Hook::ViewListener
    render_on :view_layouts_base_html_head, partial: 'hooks/ai_chat_widget_assets'
    render_on :view_layouts_base_body_bottom, partial: 'hooks/ai_chat_widget'
  end
end
