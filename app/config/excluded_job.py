excluded_job_title_keywords = [
    "Wordpress",
    "Internship",
    "Intern",
    "Web Developer",
    "Mobile App Developer"
    "Security Engineer",
    "Guidewire Digital Developer",
    "Guidewire"
    "Test Automation Engineer"
]

excluded_company_keywords = [
    "Tata Consultancy Services",
    "Lala Company",
]

def isExcludedJob(job_title: str, company_name: str) -> bool:
    for company in excluded_company_keywords:
        if company.lower() in company_name.lower():
            print(
                f"🤖 Zozo: Skipping job because company is in the exclusion list: "
                f"{company_name}"
            )
            return True

    for keyword in excluded_job_title_keywords:
        if keyword.lower() in job_title.lower():
            print(
                f"🤖 Zozo: Skipping job because job title contains an excluded keyword: "
                f"{job_title}"
            )
            return True

    return False