from django import template
from django.utils.safestring import mark_safe

register = template.Library()

BOOTSTRAP_ALERT_MAPPING = {
    'debug': 'secondary',
    'info': 'info',
    'success': 'success',
    'warning': 'warning',
    'error': 'danger',
}

@register.simple_tag(takes_context=True)
def render_messages(context):
    """Render Django messages using Bootstrap alert markup."""
    messages = context.get('messages')
    if not messages:
        return ''
    out = []
    for msg in messages:
        level_tag = getattr(msg, 'level_tag', None) or getattr(msg, 'tags', '')
        for tag in level_tag.split():
            bs = BOOTSTRAP_ALERT_MAPPING.get(tag, None)
            if bs:
                cls = bs
                break
        else:
            cls = 'info'
        html = f"<div class=\"alert alert-{cls} alert-dismissible fade show\" role=\"alert\">{msg.message}<button type=\"button\" class=\"btn-close\" data-bs-dismiss=\"alert\" aria-label=\"Close\"></button></div>"
        out.append(html)
    return mark_safe('\n'.join(out))
