import { useState, useEffect, useRef } from "react";
import axios from "axios";

const API = "http://localhost:8000";

export default function App() {
  const [docs, setDocs] = useState([]);
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const fileRef = useRef(null);
  const bottomRef = useRef(null);

  useEffect(() => { fetchDocs(); }, []);
  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  async function fetchDocs() {
    try {
      const res = await axios.get(`${API}/documents/`);
      setDocs(res.data);
    } catch {}
  }

  async function handleUpload(e) {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    const form = new FormData();
    form.append("file", file);
    try {
      const res = await axios.post(`${API}/upload/`, form);
      await fetchDocs();
      setSelectedDoc(res.data.doc_id);
      setMessages([]);
    } catch (err) {
      alert("Upload failed: " + (err.response?.data?.detail || err.message));
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  }

  function selectDoc(docId) {
    setSelectedDoc(docId);
    setMessages([]);
  }

  async function deleteDoc(docId, e) {
    e.stopPropagation();
    if (!confirm("Delete this document?")) return;
    try {
      await axios.delete(`${API}/documents/${docId}`);
      await fetchDocs();
      if (selectedDoc === docId) {
        setSelectedDoc(null);
        setMessages([]);
      }
    } catch (err) {
      alert("Delete failed: " + (err.response?.data?.detail || err.message));
    }
  }

  async function sendMessage() {
    if (!input.trim() || !selectedDoc || loading) return;
    const question = input.trim();
    setInput("");
    setMessages(prev => [...prev, { role: "user", content: question }]);
    setLoading(true);

    const assistantMsg = { role: "assistant", content: "" };
    setMessages(prev => [...prev, assistantMsg]);

    try {
      const res = await fetch(`${API}/chat/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ doc_id: selectedDoc, question }),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Server error");
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let text = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        text += decoder.decode(value, { stream: true });
        setMessages(prev => {
          const updated = [...prev];
          updated[updated.length - 1] = { role: "assistant", content: text };
          return updated;
        });
      }
    } catch (err) {
      setMessages(prev => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          role: "assistant",
          content: "⚠️ Something went wrong. Make sure the backend is running and try again.",
          isError: true
        };
        return updated;
      });
    } finally {
      setLoading(false);
    }
  }

  const activeDoc = docs.find(d => d.doc_id === selectedDoc);

  return (
    <div className="app">
      <aside className="sidebar">
        <h1>📄 DocChat</h1>
        <input type="file" accept=".pdf" ref={fileRef} onChange={handleUpload} style={{ display: "none" }} />
        <button className="upload-btn" onClick={() => fileRef.current.click()} disabled={uploading}>
          {uploading ? "Uploading..." : "+ Upload PDF"}
        </button>
        <div className="doc-list">
          {docs.length === 0 && <p className="no-docs">No documents yet</p>}
          {docs.map(doc => (
            <div key={doc.doc_id} className="doc-item-row">
              <div
                className={`doc-item ${doc.doc_id === selectedDoc ? "active" : ""}`}
                onClick={() => selectDoc(doc.doc_id)}
                title={doc.filename}
              >
                📄 {doc.filename}
              </div>
              <button
                className="delete-btn"
                onClick={(e) => deleteDoc(doc.doc_id, e)}
                title="Delete"
              >
                ✕
              </button>
            </div>
          ))}
        </div>
      </aside>

      <div className="chat-area">
        {activeDoc
          ? <div className="chat-header">Chatting with: <strong>{activeDoc.filename}</strong> ({activeDoc.page_count} pages)</div>
          : <div className="chat-header">Select a document to start chatting</div>
        }

        {!selectedDoc
          ? <div className="empty-state">Upload a PDF and ask anything about it</div>
          : <div className="messages">
              {messages.map((msg, i) => (
                <div key={i} className={`message ${msg.role}`}>
                  <div className={`bubble ${msg.isError ? "error" : ""}`}>
                    {msg.role === "assistant" && !msg.content ? "▍" : msg.content}
                  </div>
                </div>
              ))}
              <div ref={bottomRef} />
            </div>
        }

        <div className="input-area">
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === "Enter" && sendMessage()}
            placeholder={selectedDoc ? "Ask a question about the document..." : "Upload a PDF first"}
            disabled={!selectedDoc || loading}
          />
          <button className="send-btn" onClick={sendMessage} disabled={!selectedDoc || loading}>
            {loading ? "..." : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}   