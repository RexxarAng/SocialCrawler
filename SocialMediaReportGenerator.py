import jinja2
import os
from datetime import datetime


def truncate_url(url, max_length=30):
    if len(url) <= max_length:
        return url
    else:
        truncated_url = url[:max_length] + "..."
        return truncated_url


class SocialMediaReportGenerator:

    def generate_html_report(self, data):
        # Get the absolute path of the script
        script_path = os.path.abspath(__file__)

        # Get the directory containing the script
        script_dir = os.path.dirname(script_path)

        # Change the current working directory
        os.chdir(script_dir)

        # Load the HTML template
        template_loader = jinja2.FileSystemLoader(searchpath="./templates")
        template_env = jinja2.Environment(loader=template_loader)
        # Register the custom filter
        template_env.filters["truncate_url"] = truncate_url
        template = template_env.get_template("report_template_v4.html")

        # Render the template with the data
        html_output = template.render(report_data=data)

        # Create the reports folder if it doesn't exist
        os.makedirs("reports", exist_ok=True)

        # Generate the filename with current datetime
        current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"reports/social_media_report_{current_datetime}.html"

        # Save the HTML report
        with open(report_filename, 'w', encoding='utf-8') as file:
            file.write(html_output)

            # Get the absolute path of the file
            abs_path = os.path.abspath(report_filename)

            # Print the file location
            print(f"HTML report saved at: {abs_path}")
    # def generate_html_report(self, instagram_data, facebook_data, twitter_data, broken_links, unchecked_links):
    #     # Get the absolute path of the script
    #     script_path = os.path.abspath(__file__)
    #
    #     # Get the directory containing the script
    #     script_dir = os.path.dirname(script_path)
    #
    #     # Change the current working directory
    #     os.chdir(script_dir)
    #
    #     # Load the HTML template
    #     template_loader = jinja2.FileSystemLoader(searchpath="./templates")
    #     template_env = jinja2.Environment(loader=template_loader)
    #     # Register the custom filter
    #     template_env.filters["truncate_url"] = truncate_url
    #     template = template_env.get_template("report_template_v2.html")
    #
    #     report_data = {
    #         "Instagram": instagram_data,
    #         "Facebook": facebook_data,
    #         "Twitter": twitter_data
    #     }
    #     # Render the template with the data
    #     html_output = template.render(report_data=report_data, broken_links=broken_links, unchecked_links=unchecked_links)
    #
    #     # Create the reports folder if it doesn't exist
    #     os.makedirs("reports", exist_ok=True)
    #
    #     # Generate the filename with current datetime
    #     current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
    #     report_filename = f"reports/social_media_report_{current_datetime}.html"
    #
    #     # Save the HTML report
    #     with open(report_filename, 'w', encoding='utf-8') as file:
    #         file.write(html_output)
    #
    #         # Get the absolute path of the file
    #         abs_path = os.path.abspath(report_filename)
    #
    #         # Print the file location
    #         print(f"HTML report saved at: {abs_path}")
