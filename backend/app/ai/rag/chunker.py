from typing import List, Dict, Any


def chunk_extracted_pages(
    pages: List[Dict[str, Any]],
    chunk_size: int = 500,
    chunk_overlap: int = 50
) -> List[Dict[str, Any]]:
    """
    Slices extracted page text into overlapping semantic chunks from first principles.
    Preserves page_number, chunk_index, and text content.
    """
    chunks = []
    global_chunk_idx = 0

    for page_info in pages:
        page_number = page_info["page_number"]
        text = page_info["text"]

        # Split text into sentences / paragraphs first
        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]

        current_chunk = ""
        for para in paragraphs:
            if len(current_chunk) + len(para) + 1 <= chunk_size:
                current_chunk += ("\n" + para if current_chunk else para)
            else:
                if current_chunk:
                    chunks.append({
                        "chunk_index": global_chunk_idx,
                        "page_number": page_number,
                        "text": current_chunk.strip()
                    })
                    global_chunk_idx += 1

                    # Apply overlap by taking trailing slice of current_chunk
                    overlap_start = max(0, len(current_chunk) - chunk_overlap)
                    current_chunk = current_chunk[overlap_start:] + "\n" + para
                else:
                    current_chunk = para

        if current_chunk.strip():
            chunks.append({
                "chunk_index": global_chunk_idx,
                "page_number": page_number,
                "text": current_chunk.strip()
            })
            global_chunk_idx += 1

    return chunks
