import requests
import csv

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

# ask jennifer about institution ID?
def get_author_works(author_id, start_date, end_date):
    works = []
    cursor = "*"
    while True:
        # can we index while having a specific date range?
        if start_date == 0:
            url = f"https://api.openalex.org/works?filter=author.id:{author_id}&per_page=200&cursor={cursor}"
        else:
            url = f"https://api.openalex.org/works?filter=author.id:{author_id},from_publication_date:{start_date},to_publication_date:{end_date}&per_page=200&cursor={cursor}"

        r = requests.get(url)
        data = r.json()

        for work in data["results"]:
            title = work.get("title", "Unknown")
            citations = work.get("cited_by_count", 0)
            year = work.get("publication_year", None)
            journal = None
            if work.get("host_venue"):
                journal = work["host_venue"].get("display_name")

            works.append({
                "title": title,
                "citations": citations,
                "year": year,
                "journal": journal
            })
        cursor = data["meta"].get("next_cursor")

        if cursor is None:
            break

    return works


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
    # or find a system to identify author's most popular works (40% above the average citation count of author?)
    return sorted(works, key=lambda x: x["citations"], reverse=True)[:top_n]

def export_csv(papers, filename="papers.csv"):

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["title", "year", "journal", "citations"]
        )
        writer.writeheader()
        for p in papers:
            writer.writerow(p)

def analyze_researcher(orcid, start_date, end_date):
    
    author = get_openalex_author(orcid)
    works = get_author_works(author["id"], start_date, end_date)
    citation_list = [w["citations"] for w in works]
    total_citations = sum(citation_list)
    h_index = compute_h_index(citation_list)
    top_works = popular_works(works)

    return {
        "name": author["name"],
        "papers": works,
        "num_papers": len(works),
        "total_citations": total_citations,
        "top_works": top_works,
        "h_index": h_index
    }

if __name__ == "__main__":
    # replace variables as needed here:
    # author orcid, please insert as string. you can also copy-paste into an array separated by comma (i.e. orcid = ["0000-0001-7735-1341", "0000-0002-1825-0097"])
    orcid = ["0000-0001-7735-1341"]

    # specified time period, please insert as string in format "YYYY-MM-DD" (dates are inclusive)
    # if not querying, leave as "start_date = 0", "end_date = 0" -> integers, not strings
    start_date = "2023-01-01"
    end_date = "2026-03-02"

    for id in orcid:
        data = analyze_researcher(id, start_date, end_date)

        print("\nResearcher:", data["name"])
        print("Number of papers:", data["num_papers"])
        print("Total citations:", data["total_citations"])
        print("Citation list:", [p["citations"] for p in data["papers"]])
        print("h-index:", data["h_index"])
        print("\nTop 2 papers:")
        for work in data["top_works"]:
            print(f"  - {work['title']} ({work['citations']} citations)")

        # TODO: export as file that can be transferred to excel database 
        #export_csv(data["papers"])

        #print("\nPaper list saved to papers.csv")
