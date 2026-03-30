"use client";
import { useEffect, useState, useRef } from "react";
import AppLayout from "@/components/layout/AppLayout";
import LoadingSpinner from "@/components/ui/LoadingSpinner";
import { importsApi, platformsApi } from "@/lib/api";
import { Platform } from "@/types";
import { cn } from "@/lib/utils";
import { Upload, FileText, CheckCircle, XCircle, Clock, Eye, Play, AlertCircle } from "lucide-react";

const PARSERS = [
  { value: "generic_brokerage", label: "Generic Brokerage CSV" },
  { value: "generic_deal", label: "Generic Deal CSV" },
  { value: "derayah", label: "Derayah" },
  { value: "alrajhi", label: "Al Rajhi" },
  { value: "alinma", label: "Alinma" },
  { value: "tamra", label: "Tamra" },
  { value: "aseel", label: "Aseel" },
  { value: "sukuk", label: "Sukuk" },
  { value: "manafa", label: "Manafa" },
  { value: "safqah", label: "Safqah" },
  { value: "tarmeez", label: "Tarmeez" },
  { value: "awaed", label: "Awaed" },
  { value: "derayah_smart", label: "Derayah Smart" },
];

function StatusBadge({ status }: { status: string }) {
  const cfg: Record<string, { color: string; icon: React.ElementType }> = {
    completed: { color: "bg-emerald-100 text-emerald-700", icon: CheckCircle },
    failed: { color: "bg-red-100 text-red-700", icon: XCircle },
    partial: { color: "bg-amber-100 text-amber-700", icon: AlertCircle },
    pending: { color: "bg-gray-100 text-gray-600", icon: Clock },
    processing: { color: "bg-blue-100 text-blue-700", icon: Clock },
    preview: { color: "bg-purple-100 text-purple-700", icon: Eye },
  };
  const { color, icon: Icon } = cfg[status] || cfg.pending;
  return (
    <span className={cn("badge gap-1", color)}>
      <Icon className="w-3 h-3" />
      {status}
    </span>
  );
}

export default function ImportsPage() {
  const [imports, setImports] = useState<any[]>([]);
  const [platforms, setPlatforms] = useState<Platform[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [preview, setPreview] = useState<{ id: number; rows: any[] } | null>(null);
  const [running, setRunning] = useState<number | null>(null);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);

  // Form state
  const [platformId, setPlatformId] = useState("");
  const [parser, setParser] = useState("generic_brokerage");

  useEffect(() => {
    Promise.all([importsApi.list(), platformsApi.list()])
      .then(([imp, plt]) => {
        setImports(imp.data);
        setPlatforms(plt.data);
        if (plt.data.length > 0) setPlatformId(String(plt.data[0].id));
      })
      .finally(() => setLoading(false));
  }, []);

  async function handleUpload(e: React.FormEvent) {
    e.preventDefault();
    const file = fileRef.current?.files?.[0];
    if (!file || !platformId) return;

    const fd = new FormData();
    fd.append("file", file);
    fd.append("platform_id", platformId);
    fd.append("parser_name", parser);

    setUploading(true);
    setError("");
    try {
      const res = await importsApi.upload(fd);
      const id = res.data.raw_import_id;
      const imp = await importsApi.list();
      setImports(imp.data);
      setSuccess(`File uploaded (id: ${id}). Preview it below.`);
      if (fileRef.current) fileRef.current.value = "";
    } catch (e: any) {
      setError(e.response?.data?.detail || "Upload failed");
    } finally {
      setUploading(false);
    }
  }

  async function handlePreview(id: number) {
    try {
      const res = await importsApi.preview(id);
      setPreview({ id, rows: res.data.rows });
    } catch (e: any) {
      setError(e.response?.data?.detail || "Preview failed");
    }
  }

  async function handleRun(id: number) {
    setRunning(id);
    setError("");
    setSuccess("");
    try {
      const res = await importsApi.run(id);
      setSuccess(`Import complete: ${res.data.rows_imported} rows imported, ${res.data.rows_failed} failed.`);
      const imp = await importsApi.list();
      setImports(imp.data);
      setPreview(null);
    } catch (e: any) {
      setError(e.response?.data?.detail || "Import failed");
    } finally {
      setRunning(null);
    }
  }

  if (loading) return <AppLayout><LoadingSpinner /></AppLayout>;

  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Data Imports</h1>
          <p className="text-sm text-gray-500 mt-0.5">Upload CSV or Excel files to import transactions and deal data</p>
        </div>

        {error && <div className="flex items-center gap-2 text-red-600 bg-red-50 px-4 py-3 rounded-lg text-sm"><XCircle className="w-4 h-4" /> {error}</div>}
        {success && <div className="flex items-center gap-2 text-emerald-600 bg-emerald-50 px-4 py-3 rounded-lg text-sm"><CheckCircle className="w-4 h-4" /> {success}</div>}

        {/* Upload form */}
        <div className="card">
          <h2 className="text-sm font-semibold text-gray-700 mb-4 flex items-center gap-2">
            <Upload className="w-4 h-4" /> Upload File
          </h2>
          <form onSubmit={handleUpload} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Platform</label>
                <select
                  value={platformId}
                  onChange={(e) => setPlatformId(e.target.value)}
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                  required
                >
                  {platforms.map((p) => (
                    <option key={p.id} value={p.id}>{p.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Parser</label>
                <select
                  value={parser}
                  onChange={(e) => setParser(e.target.value)}
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                >
                  {PARSERS.map((p) => (
                    <option key={p.value} value={p.value}>{p.label}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">File</label>
                <input
                  ref={fileRef}
                  type="file"
                  accept=".csv,.xlsx,.xls"
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm file:mr-2 file:text-xs file:bg-gray-100 file:border-0 file:rounded file:px-2 file:py-1"
                  required
                />
              </div>
            </div>
            <div className="flex gap-3 pt-1">
              <button type="submit" disabled={uploading} className="btn-primary">
                {uploading ? "Uploading..." : "Upload"}
              </button>
              <p className="text-xs text-gray-400 self-center">
                CSV/XLSX up to 50 MB. Download templates below.
              </p>
            </div>
          </form>
        </div>

        {/* Preview panel */}
        {preview && (
          <div className="card">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm font-semibold text-gray-700 flex items-center gap-2">
                <Eye className="w-4 h-4" /> Preview (first 20 rows)
              </h2>
              <div className="flex gap-2">
                <button
                  onClick={() => handleRun(preview.id)}
                  disabled={running === preview.id}
                  className="btn-primary flex items-center gap-1 text-xs"
                >
                  <Play className="w-3 h-3" />
                  {running === preview.id ? "Importing..." : "Run Import"}
                </button>
                <button onClick={() => setPreview(null)} className="btn-secondary text-xs">Dismiss</button>
              </div>
            </div>
            {preview.rows.length === 0 ? (
              <p className="text-sm text-gray-500">No rows parsed. Check the file format and parser selection.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b border-gray-100">
                      {Object.keys(preview.rows[0]).map((k) => (
                        <th key={k} className="px-3 py-2 text-left text-gray-500 font-medium">{k}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-50">
                    {preview.rows.map((row, i) => (
                      <tr key={i} className="hover:bg-gray-50">
                        {Object.values(row).map((val: any, j) => (
                          <td key={j} className="px-3 py-2 text-gray-700">{String(val)}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* Import history */}
        <div className="card p-0">
          <div className="px-5 py-4 border-b border-gray-100">
            <h2 className="text-sm font-semibold text-gray-700 flex items-center gap-2">
              <FileText className="w-4 h-4" /> Import History
            </h2>
          </div>
          {imports.length === 0 ? (
            <div className="px-5 py-8 text-center text-sm text-gray-400">No imports yet</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-50 text-left">
                    {["File", "Parser", "Status", "Imported", "Failed", "Date", "Actions"].map((h) => (
                      <th key={h} className="px-4 py-3 text-xs font-semibold text-gray-500">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {imports.map((imp) => (
                    <tr key={imp.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 max-w-[180px] truncate text-gray-800">{imp.filename.split("_").slice(2).join("_") || imp.filename}</td>
                      <td className="px-4 py-3 text-gray-500 text-xs">{imp.parser_name}</td>
                      <td className="px-4 py-3"><StatusBadge status={imp.import_status} /></td>
                      <td className="px-4 py-3 text-emerald-600">{imp.rows_imported ?? "—"}</td>
                      <td className="px-4 py-3 text-red-500">{imp.rows_failed ?? "—"}</td>
                      <td className="px-4 py-3 text-gray-400 text-xs">
                        {imp.created_at ? new Date(imp.created_at).toLocaleDateString() : "—"}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex gap-1">
                          {["pending", "preview"].includes(imp.import_status) && (
                            <button
                              onClick={() => handlePreview(imp.id)}
                              className="btn-secondary text-xs py-1 px-2"
                            >
                              Preview
                            </button>
                          )}
                          {imp.import_status === "preview" && (
                            <button
                              onClick={() => handleRun(imp.id)}
                              disabled={running === imp.id}
                              className="btn-primary text-xs py-1 px-2"
                            >
                              Run
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Template downloads */}
        <div className="card bg-gray-50 border-dashed">
          <h3 className="text-sm font-semibold text-gray-600 mb-2">Import Templates</h3>
          <p className="text-xs text-gray-500 mb-3">Download and fill these templates, then upload using the matching parser.</p>
          <div className="flex gap-3">
            <a href="/templates/brokerage_standard_template.csv" download className="btn-secondary text-xs">
              Brokerage Template
            </a>
            <a href="/templates/deal_standard_template.csv" download className="btn-secondary text-xs">
              Deal Template
            </a>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
