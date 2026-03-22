import requests
import csv
import re

def get_openalex_author(orcid):
    url = f"https://api.openalex.org/authors?filter=orcid:{orcid}"

    r = requests.get(url)
    data = r.json()

    if data["meta"]["count"] == 0:
        raise Exception("Author not found in OpenAlex")

    author = data["results"][0]

    return {
        "id": author["id"],
        "name": author["display_name"]
    }

def get_author_name(author_id):
    if author_id.startswith("https://"):
        author_id = author_id.split("/")[-1]

    url = f"https://api.openalex.org/authors/{author_id}"
    
    r = requests.get(url)
    data = r.json()

    return data.get("display_name", "Unknown")

def get_author_works(author_id, start_date, end_date):
    works = []
    cursor = "*"
    institution_counts = {}
    while True:
        if start_date == 0:
            url = f"https://api.openalex.org/works?filter=author.id:{author_id}&per_page=200&cursor={cursor}"
        else:
            url = f"https://api.openalex.org/works?filter=author.id:{author_id},from_publication_date:{start_date},to_publication_date:{end_date}&per_page=200&cursor={cursor}"

        r = requests.get(url)
        data = r.json()

        for work in data["results"]:
            title = work.get("title", "Unknown")
            citations = work.get("cited_by_count", 0)
            date = work.get("publication_date", None)
            biblio = work.get("biblio", {})
            issue = biblio.get("issue")
            authors = []
            for authorship in work.get("authorships", []):
                author = authorship.get("author", {})
                authors.append(author.get("display_name", "Unknown"))

            journal = None
            primary_location = work.get("primary_location")

            if primary_location and primary_location.get("source"):
                journal = primary_location["source"].get("display_name")

            for authorship in work.get("authorships", []):
                author = authorship.get("author", {})

                if author.get("id", "").endswith(author_id.split("/")[-1]):

                    for inst in authorship.get("institutions", []):
                        name = inst.get("display_name", "Unknown")

                        institution_counts[name] = institution_counts.get(name, 0) + 1

            works.append({
                "title": title,
                "citations": citations,
                "authors": authors,
                "publication date": date,
                "journal": journal,
                "issue": issue
            })
        cursor = data["meta"].get("next_cursor")
        if cursor is None:
            break
    return works, institution_counts

def compute_h_index(citations):
    citations_sorted = sorted(citations, reverse=True)
    h = 0
    for i, c in enumerate(citations_sorted):
        if c >= i + 1:
            h = i + 1
        else:
            break
    return h

def popular_works(works, top_n=2):
    return sorted(works, key=lambda x: x["citations"], reverse=True)[:top_n]

def journal_count(works):
    journal_dict = {}
    for work in works:
        journal = work["journal"] if work["journal"] else "Unknown"
        journal_dict[journal] = journal_dict.get(journal, 0) + 1
    return journal_dict

# only include list of institutions that researcher's associated institutions -> focus on hospitals
# ask jennifer if current institutions is more accurate?
def export_csv_curated(all_data, savefile):
    with open(savefile, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["researcher", "num_papers", "total_citations", "h_index"]
        )
        writer.writeheader()
        for data in all_data:
            writer.writerow({
                "researcher": data["name"],
                "num_papers": data["num_papers"],
                "total_citations": data["total_citations"],
                "h_index": data["h_index"]
            })

# includes data from above, as well as total journal counts, institution counts, and list of papers.
# use this if checking publications in a date range for papers -> full citation title, journal, issue, date, authors // separate file 
def export_csv_raw(all_data, savefile):
    with open(savefile, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["researcher", "num_papers", "total_citations", "h_index", "institutions", "journal_counts", "papers"]
        )
        writer.writeheader()
        for data in all_data:
            writer.writerow({
                "researcher": data["name"],
                "num_papers": data["num_papers"],
                "total_citations": data["total_citations"],
                "h_index": data["h_index"],
                "institutions": data["institutions"],
                "journal_counts": data["journal_counts"],
                "papers": data["papers"]
            })

def analyze_researcher(orcid, start_date, end_date):
    if re.match(r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$", orcid) is not None:
        author = get_openalex_author(orcid)
        author_id = author["id"]
        author_name = author["name"]
    else:
        author_id = orcid
        author_name = get_author_name(author_id)

    works, institution_counts = get_author_works(author_id, start_date, end_date)
    citation_list = [w["citations"] for w in works]
    total_citations = sum(citation_list)
    h_index = compute_h_index(citation_list)
    top_works = popular_works(works)
    journal_counts = journal_count(works)
    # if "Unknown" in journal_counts: del journal_counts["Unknown"] # uncomment out if you wish to delete unknown journal entries

    return {
        "name": author_name, 
        "papers": works,
        "num_papers": len(works),
        "total_citations": total_citations,
        "top_works": top_works,
        "h_index": h_index,
        "journal_counts": journal_counts, 
        "institutions": institution_counts
    }

if __name__ == "__main__":
    # replace variables as needed here:
    # author orcid, please insert as string. you can also copy-paste into an array separated by comma (i.e. orcid = ["0000-0001-7735-1341", "0000-0002-1825-0097"])
    # please also insert any openalex IDs here by taking the 11 character code after the profile's main URL (i.e. https://openalex.org/A1234567890 -> "A1234567890")
    orcid = ["0000-0001-7735-1341", "0009-0005-6618-9795", "A5060582284", "A5113863381"]

    # specified time period, please insert as string in format "YYYY-MM-DD" (dates are inclusive)
    # if not querying, leave as "start_date = 0", "end_date = 0" -> integers, not strings
    start_date = 0
    end_date = "2026-03-02"

    # change savefile name if needed, defaults are as listed. your previous files may be overwritten if you use the same name.
    savefile_raw = "CRAFT_authors_raw.csv"
    savefile_curated = "CRAFT_authors_curated.csv"

    all_data = []

    for id in orcid:
        data = analyze_researcher(id, start_date, end_date)
        all_data.append(data)

        # uncomment out only if you wish to print out the data in the terminal, otherwise it will only be saved in the csv files.
        '''if start_date != 0:
            print(f"\nInformation from {start_date} to {end_date} (YYYY-MM-DD):")
        print("\nResearcher:", data["name"])
        print("Number of papers:", data["num_papers"])
        print("Total citations:", data["total_citations"])
        print("h-index:", data["h_index"])
        print("Journal counts:", data["journal_counts"])
        print("Institutions:", data["institutions"])
        print("\nTop 2 papers:")
        for work in data["top_works"]:
            print(f"  - {work['title']} ({work['citations']} citations)")'''
    # uncomment the following lines to save to specific csvs.
    export_csv_curated(all_data, savefile_curated)
    print(f"\nResearcher data saved to {savefile_curated}")
    export_csv_raw(all_data, savefile_raw)
    print(f"\nResearcher data saved to {savefile_raw}")
