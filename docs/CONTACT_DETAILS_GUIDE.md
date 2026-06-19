# 📞 Contact Details Management Guide

## Overview

The contact details feature allows you to manage contact information that appears in the footer and about page of your website. All contact details are stored in the database and can be managed through the admin panel.

## ✨ Features

- **Dynamic Footer**: Contact details automatically appear in the website footer
- **Admin Management**: Full CRUD operations through the admin panel
- **Icon Support**: Font Awesome icons for each contact detail
- **Link Support**: Clickable links for email, phone, social media, etc.
- **Ordering**: Control the display order of contact details
- **Active/Inactive**: Toggle contact details on/off

## 🚀 Quick Setup

### 1. Add Default Contact Details

Run the setup script to add default contact details:

```bash
python helper/add_default_contact_details.py
```

This will add:
- Email: info.sindikasimedia@gmail.com
- WhatsApp: +62 812-3456-7890
- Address: Jl. Contoh No. 123, Jakarta
- Phone: +62 21-1234-5678
- Facebook: Sindikasi Media
- Instagram: @sindikasimedia

### 2. Access Admin Panel

1. Log in to your admin account
2. Go to **Settings** > **Detail Kontak**
3. Manage your contact details

## 📋 Managing Contact Details

### Adding New Contact Details

1. Go to **Settings** > **Detail Kontak**
2. Fill in the form:
   - **Judul**: Display name (e.g., "Email", "WhatsApp")
   - **Konten**: The actual contact information
   - **Urutan Bagian**: Display order (1, 2, 3, etc.)
   - **Kelas Ikon**: Font Awesome icon class (e.g., "envelope", "phone")
   - **Tautan**: URL or link (e.g., "mailto:email@example.com")
3. Click **Tambah Detail Kontak**

### Available Icons

The system supports these Font Awesome icons:
- `envelope` - Email
- `phone` - Phone
- `map-marker-alt` - Location/Address
- `facebook` - Facebook
- `twitter` - Twitter
- `instagram` - Instagram
- `linkedin` - LinkedIn
- `whatsapp` - WhatsApp
- `youtube` - YouTube
- `github` - GitHub
- `skype` - Skype
- `telegram` - Telegram
- `pinterest` - Pinterest

### Link Formats

Use these link formats for different contact types:

- **Email**: `mailto:email@example.com`
- **Phone**: `tel:+1234567890`
- **WhatsApp**: `https://wa.me/1234567890`
- **Social Media**: `https://facebook.com/username`
- **Website**: `https://example.com`

### Editing Contact Details

1. Find the contact detail you want to edit
2. Modify the fields as needed
3. Check/uncheck **Aktif** to enable/disable
4. Click **Perbarui**

### Deleting Contact Details

1. Find the contact detail you want to delete
2. Click **Hapus**
3. Confirm the deletion

## 🎨 Display Features

### Footer Display

Contact details appear in the footer with:
- Icons (if specified)
- Clickable links (if provided)
- Proper formatting
- Fallback to default email if no contact details exist

### About Page Display

Contact details also appear on the About page in a dedicated contact section.

### Responsive Design

- Desktop: Icons and text side by side
- Mobile: Stacked layout for better readability

## 🔧 Technical Details

### Database Model

```python
class ContactDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    section_order = db.Column(db.Integer, nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    icon_class = db.Column(db.String(100), nullable=True)
    link = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=default_utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=default_utcnow, onupdate=default_utcnow, nullable=False)
```

### Template Usage

Contact details are automatically available in all templates via the `contact_details` variable:

```html
{% if contact_details %}
  {% for detail in contact_details %}
    {% if detail.is_active %}
      <li>
        {% if detail.link %}
          <a href="{{ detail.link }}">
            {% if detail.icon_class %}
              <i class="fas fa-{{ detail.icon_class }}"></i>
            {% endif %}
            {{ detail.title }}: {{ detail.content }}
          </a>
        {% else %}
          <span>
            {% if detail.icon_class %}
              <i class="fas fa-{{ detail.icon_class }}"></i>
            {% endif %}
            {{ detail.title }}: {{ detail.content }}
          </span>
        {% endif %}
      </li>
    {% endif %}
  {% endfor %}
{% endif %}
```

## 🎯 Best Practices

1. **Order Matters**: Use section_order to control display sequence
2. **Icons Help**: Add appropriate icons for better visual appeal
3. **Links Work**: Use proper link formats for clickable contact info
4. **Keep Active**: Only show contact details that are currently valid
5. **Test Links**: Verify all links work correctly before making them active

## 🚨 Troubleshooting

### Contact Details Not Showing

1. Check if contact details exist in the database
2. Verify that `is_active` is set to `True`
3. Check the admin panel for any errors
4. Ensure the context processor is working

### Icons Not Displaying

1. Verify Font Awesome is loaded (already included in base template)
2. Check that icon_class values are valid Font Awesome classes
3. Ensure the icon class doesn't have the `fa-` prefix (it's added automatically)

### Links Not Working

1. Verify link format is correct
2. Test links in a new browser tab
3. Check for typos in URLs
4. Ensure external links have proper protocols (http://, https://)

## 📞 Support

If you need help with contact details management:
1. Check the admin panel for error messages
2. Verify database connectivity
3. Review the contact details settings page
4. Contact your system administrator

---

**Your contact details are now fully dynamic and manageable through the admin panel!** 🎉 