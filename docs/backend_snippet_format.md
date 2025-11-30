# Backend Response Example for Snippets

This document shows an example of the expected backend response format for the `/chat` endpoint.

## Example Chat Request

```json
{
  "query": "What are the main benefits of active learning in machine learning?"
}
```

## Example Chat Response

```json
{
  "summary": "Active learning offers several key benefits for machine learning systems. First, it significantly reduces the amount of labeled data needed to achieve good model performance, which is crucial since data labeling is often expensive and time-consuming [1]. Second, active learning allows the model to intelligently select the most informative examples for labeling, leading to more efficient use of labeling resources [1][2]. Third, studies have shown that active learning can achieve comparable or better performance than passive learning with only a fraction of the labeled data [2][3].",
  
  "citations": [
    {
      "id": 1,
      "title": "Active Learning Literature Survey",
      "authors": "Settles, B.",
      "year": "2009",
      "pdf_path": "/Users/username/Zotero/storage/ABC123/Settles_2009.pdf"
    },
    {
      "id": 2,
      "title": "Practical Considerations in Active Learning",
      "authors": "Bloodgood, M., Vijay-Shanker, K.",
      "year": "2009",
      "pdf_path": "/Users/username/Zotero/storage/DEF456/Bloodgood_2009.pdf"
    },
    {
      "id": 3,
      "title": "Active Learning with Support Vector Machines",
      "authors": "Tong, S., Koller, D.",
      "year": "2001",
      "pdf_path": "/Users/username/Zotero/storage/GHI789/Tong_2001.pdf"
    }
  ],
  
  "snippets": [
    {
      "id": "1:42",
      "citation_id": 1,
      "snippet": "The key idea behind active learning is that a machine learning algorithm can achieve greater accuracy with fewer training labels if it is allowed to choose the data from which it learns. An active learner may pose queries, usually in the form of unlabeled data instances to be labeled by an oracle (e.g., a human annotator).",
      "title": "Active Learning Literature Survey",
      "authors": "Settles, B.",
      "year": "2009",
      "pdf_path": "/Users/username/Zotero/storage/ABC123/Settles_2009.pdf"
    },
    {
      "id": "1:43",
      "citation_id": 1,
      "snippet": "There are situations in which unlabeled data is abundant but labels are difficult, time-consuming, or expensive to obtain. In such cases, active learning can be of great practical value. For example, in many natural language processing tasks, obtaining unlabeled data is relatively inexpensive (e.g., web pages, news articles), but labeling can require significant human effort.",
      "title": "Active Learning Literature Survey",
      "authors": "Settles, B.",
      "year": "2009",
      "pdf_path": "/Users/username/Zotero/storage/ABC123/Settles_2009.pdf",
      "page": 3
    },
    {
      "id": "2:15",
      "citation_id": 2,
      "snippet": "We investigate the effectiveness of active learning in a real-world setting and find that uncertainty sampling can reduce annotation cost by up to 50% while maintaining the same level of model performance. This result demonstrates that active learning is not only theoretically sound but also practically useful in reducing the human effort required for supervised learning.",
      "title": "Practical Considerations in Active Learning",
      "authors": "Bloodgood, M., Vijay-Shanker, K.",
      "year": "2009",
      "pdf_path": "/Users/username/Zotero/storage/DEF456/Bloodgood_2009.pdf",
      "page": 7
    },
    {
      "id": "3:28",
      "citation_id": 3,
      "snippet": "Our experiments with support vector machines show that active learning can select training examples that are near the decision boundary, which are typically the most informative for defining the optimal separating hyperplane. This targeted selection strategy allows the SVM to achieve 95% of its full-data accuracy with only 20-30% of the training data.",
      "title": "Active Learning with Support Vector Machines",
      "authors": "Tong, S., Koller, D.",
      "year": "2001",
      "pdf_path": "/Users/username/Zotero/storage/GHI789/Tong_2001.pdf",
      "page": 12
    }
  ]
}
```

## Field Descriptions

### Citation Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | number | Yes | Unique citation ID (1-based) used to reference this source |
| `title` | string | Yes | Full title of the paper/book |
| `authors` | string | No | Author names (comma-separated or formatted string) |
| `year` | string/number | No | Publication year |
| `pdf_path` | string | No | Local file system path to the PDF |

### Snippet Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique snippet ID (typically `{item_id}:{chunk_idx}`) |
| `citation_id` | number | Yes | References the citation this snippet came from |
| `snippet` | string | Yes | The actual text chunk from the document |
| `title` | string | No | Item title (usually matches citation) |
| `authors` | string | No | Item authors (usually matches citation) |
| `year` | string/number | No | Publication year (usually matches citation) |
| `pdf_path` | string | No | Path to PDF (usually matches citation) |
| `page` | number/string | No | Page number where this snippet appears |

## Notes

1. **Citation IDs**: Should be sequential integers starting from 1. These are used in the summary text as `[1]`, `[2]`, etc.

2. **Snippet IDs**: Should be globally unique. The backend currently uses `{item_id}:{chunk_idx}` format.

3. **Redundant Metadata**: Snippets include `title`, `authors`, `year`, and `pdf_path` even though they're in the citation. This allows the frontend to display snippet cards without requiring a citation lookup, and provides flexibility for cases where snippet-level metadata might differ (e.g., different page numbers, different editions).

4. **Page Numbers**: Optional but highly valuable for user navigation. Should be included when available from the chunking/indexing process.

5. **Order Matters**: Snippets should be ordered by relevance (most relevant first), as this is how they'll be displayed in the UI.

6. **Text Length**: Snippets can be any length, but ~600-1000 characters is ideal for display. The frontend will truncate to 350 characters with a "Show more" option.

## Backend Implementation

The current backend implementation in `backend/interface.py` already follows this format:

```python
def chat(self, query, filter_item_ids=None):
    # ... retrieval logic ...
    
    snippets.append({
        "citation_id": cid,
        "snippet": snippet_text,
        "title": title,
        "year": year,
        "authors": authors,
        "pdf_path": pdf_path,
    })
    
    citations = [
        {
            "id": cid,
            "title": title,
            "year": year,
            "authors": authors,
            "pdf_path": pdf_path,
        }
        for (title, year, pdf_path), cid in citation_map.items()
    ]
    
    return {
        "summary": summary,
        "citations": citations,
        "snippets": snippets,
    }
```

## Testing the Response

To test that your backend is returning the correct format:

```bash
# Start the backend
cd backend
python main.py

# In another terminal, test the endpoint
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is active learning?"}'
```

Verify that the response includes:
- `summary` string
- `citations` array with proper IDs
- `snippets` array with `snippet` text and `citation_id` references
