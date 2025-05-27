import csv
import re
import dns.resolver
from urllib.parse import urlparse

def extract_domain_from_email(email):
    try:
        return email.split('@')[1]
    except:
        return None

def extract_domain_from_website(website):
    if not website:
        return None
    try:
        parsed = urlparse(website if website.startswith('http') else f'http://{website}')
        return parsed.netloc
    except:
        return None

def get_mail_provider(domain):
    if not domain:
        return None
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        mx_hosts = [str(x.exchange).rstrip('.').lower() for x in mx_records]
        
        # Extract main domain from first MX record
        if mx_hosts:
            mx_domain = '.'.join(mx_hosts[0].split('.')[-2:])
            
            # Check for known providers
            if any(host.endswith(('google.com', 'gmail.com', 'googlemail.com')) for host in mx_hosts):
                return 'google'
            elif any(host.endswith(('outlook.com', 'hotmail.com', 'microsoft.com')) for host in mx_hosts):
                return 'microsoft'
            elif any(host.endswith(('vnn.vn', 'vnpt.vn', 'viettel.vn', 'fpt.vn')) for host in mx_hosts):
                return 'vietnam'
            else:
                return mx_domain
    except:
        return None

def is_tech_company(company_name, business_type):
    tech_keywords = [
        'công nghệ', 'phần mềm', 'it ', 'software', 'tech', 'digital',
        'website', 'internet', 'online', 'web', 'cloud', 'computer',
        'system', 'data', 'information', 'computing', 'solution',
        'network', 'cyber', 'security', 'ai', 'artificial', 'intelligence',
        'machine learning', 'automation', 'robotics', 'blockchain',
        'crypto', 'fintech', 'telecom', 'telecommunication', 'mobile',
        'app', 'application', 'developer', 'programming', 'code',
        'developer', 'programmer', 'coder', 'analytics', 'analysis',
        'consulting', 'consultant', 'service', 'technology', 'digital',
        'innovation', 'startup', 'entrepreneur', 'entrepreneurship',
        'Thương mại điện tử', 'thương mại điện tử', 'thương mại điện tử',
        'thương mại điện tử', 'thương mại điện tử', 'thương mại điện tử',
        'TMĐT', 'tmđt', 'tmđt', 'tmđt', 'tmđt', 'tmđt', 'tmđt',
        'ecommerce', 'e-commerce', 'e commerce', 'e-commerce',
        
    ]
    
    if not company_name or not business_type:
        return False
        
    text = (company_name + ' ' + business_type).lower()
    return any(keyword in text for keyword in tech_keywords)

def main():
    rows = []
    
    with open('/Users/tungnt/Documents/customer.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=';')
        headers = reader.fieldnames + [
            'Có thể tư vấn Email transaction (tech company)',
            'Có thể tư vấn Business Email',
            'Email provider hiện tại'
        ]
        
        for row in reader:
            email = row['Email TK']
            company = row['Tên Công ty']
            website = row['Website']
            business = row['Ngành nghề']
            
            email_domain = extract_domain_from_email(email)
            website_domain = extract_domain_from_website(website)
            domain = website_domain or email_domain
            
            # Get provider and check if tech company
            provider = get_mail_provider(domain) if domain else None
            is_tech = is_tech_company(company, business)
            
            # Add new columns
            row['Có thể tư vấn Email transaction (tech company)'] = 'Có' if is_tech else 'Không'
            row['Có thể tư vấn Business Email'] = 'Có' if company and domain else 'Không'
            row['Email provider hiện tại'] = provider if provider else 'Chưa xác định'
            
            rows.append(row)
    
    # Write back to CSV with additional columns
    output_file = 'customer_analyzed.csv'
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"\nExported results to: {output_file}")

if __name__ == "__main__":
    main()