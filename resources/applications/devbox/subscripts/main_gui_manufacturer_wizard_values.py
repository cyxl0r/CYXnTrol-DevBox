from __future__ import annotations

from subscripts.main_gui_devbox_log import get_devbox_logger
LOGGER = get_devbox_logger(__file__)
LOGGER.info("Module loaded.")


from html import escape


def manufacturer_values(wizard) -> dict[str, object]:
    name = wizard.manufacturer_name.text().strip()
    organization_type = wizard.organization_type()
    organization_name = wizard.organization_name.text().strip()
    owner_name = wizard.owner_name.text().strip()
    return {
        "manufacturer_name": name,
        "manufacturer_display_name": name,
        "manufacturer_brand_name": name,
        "product_family": wizard.product_family,
        "founded_year": int(wizard.founded_year.value()),
        "organization_type": organization_type,
        "organization_name": organization_name if organization_type == "formal_organization" else None,
        "manufacturer_legal_name": organization_name if organization_type == "formal_organization" else None,
        "owner_name": owner_name if organization_type == "fantasy_organization" else None,
        "author_name": wizard.author_name.text().strip(),
        "author_display_name": wizard.author_display_name.text().strip(),
        "publisher_name": wizard.publisher_name.text().strip(),
        "developer_name": wizard.developer_name.text().strip(),
        "vendor_name": wizard.vendor_name.text().strip() or None,
        "country": wizard.country.text().strip(),
        "country_code": wizard.country_code.text().strip().upper(),
        "region": wizard.region.text().strip() or None,
        "city": wizard.city.text().strip() or None,
        "website_url": wizard.website_url.text().strip() or None,
        "contact_email": wizard.contact_email.text().strip() or None,
        "support_email": wizard.support_email.text().strip() or None,
        "support_url": wizard.support_url.text().strip() or None,
        "privacy_policy_url": wizard.privacy_policy_url.text().strip() or None,
        "terms_url": wizard.terms_url.text().strip() or None,
    }


def devbox_values(wizard) -> dict[str, object]:
    return {
        "author": wizard.devbox_author.text().strip(),
        "publisher": wizard.devbox_publisher.text().strip(),
        "vendor": wizard.devbox_vendor.text().strip() or None,
        "copyright_holder": wizard.devbox_copyright_holder.text().strip(),
        "country": wizard.country.text().strip(),
        "country_code": wizard.country_code.text().strip().upper(),
        "homepage_url": wizard.devbox_homepage_url.text().strip() or None,
        "support_url": wizard.devbox_support_url.text().strip() or None,
        "license_name": "Zero-Clause BSD License",
        "license_version": "0BSD",
    }


def summary_html(manufacturer: dict[str, object], devbox: dict[str, object]) -> str:
    formal = manufacturer["organization_type"] == "formal_organization"
    type_label = "Formale Organisation" if formal else "Fantasie- / Markenorganisation"
    relation_label = "Organisation" if formal else "Person dahinter"
    relation_value = manufacturer["organization_name"] if formal else manufacturer["owner_name"]
    website = manufacturer["website_url"] or "nicht angegeben"
    support = manufacturer["support_email"] or manufacturer["support_url"] or "nicht angegeben"
    return (
        "<b>Manufaktur-Ersteinrichtung</b><br><br>"
        f"<b>Produktfamilie:</b> {escape(str(manufacturer['product_family']))}<br>"
        f"<b>Manufaktur / Dachname:</b> {escape(str(manufacturer['manufacturer_name']))}<br>"
        f"<b>Gründungsjahr:</b> {manufacturer['founded_year']}<br>"
        f"<b>Land:</b> {escape(str(manufacturer['country']))} "
        f"({escape(str(manufacturer['country_code']))})<br>"
        f"<b>Organisationsform:</b> {type_label}<br>"
        f"<b>{relation_label}:</b> {escape(str(relation_value or ''))}<br>"
        f"<b>Website:</b> {escape(str(website))}<br>"
        f"<b>Support:</b> {escape(str(support))}<br><br>"
        "<b>DevBox</b><br>"
        f"<b>Autor:</b> {escape(str(devbox['author']))}<br>"
        f"<b>Herausgeber:</b> {escape(str(devbox['publisher']))}<br>"
        f"<b>Copyright:</b> {escape(str(devbox['copyright_holder']))}<br>"
        f"<b>Lizenz:</b> {escape(str(devbox['license_name']))} "
        f"({escape(str(devbox['license_version']))})<br><br>"
        "<b>Automatisch:</b> Manufaktur-ID, Zeitstempel, Aktivstatus und die "
        "Produktfamilie aus dem Projektroot werden ergänzt."
    )
