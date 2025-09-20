"use client";
import React, { useEffect, useState } from 'react';
import api from '@/lib/api';
import dynamic from 'next/dynamic';
const ReactEcharts = dynamic(async () => (await import('echarts-for-react')).default, { ssr: false, loading: () => <div>Loading chart…</div> });

type Claim = {
  id: number;
  claim_id: string;
  status: string;
  error_type: string;
  error_explanation: string;
  recommended_action: string;
  paid_amount_aed: string | number;
};

type Metrics = {
  counts_by_error: Record<string, number>;
  paid_by_error: Record<string, number>;
};

export default function DashboardPage() {
  const [claims, setClaims] = useState<Claim[]>([]);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [tenant, setTenant] = useState('');
  const [jobs, setJobs] = useState<any[]>([]);

  const fetchResults = async () => {
    const r = await api.get('/results/');
    setClaims(r.data.claims || []);
    setMetrics(r.data.metrics || null);
  };
  const fetchAudit = async () => {
    const r = await api.get('/audit/');
    setJobs(r.data.jobs || []);
  };

  useEffect(() => {
    const tid = localStorage.getItem('tenantId') || '';
    setTenant(tid);
    fetchResults();
    fetchAudit();
  }, []);

  const uploadClaims = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = e.currentTarget;
    const fileInput = form.querySelector<HTMLInputElement>('input[name="claims"]');
    if (!fileInput?.files?.[0]) return;
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    await api.post('/upload/claims/', formData, { headers: { 'Content-Type': 'multipart/form-data' } });
    await fetchResults();
    await fetchAudit();
  };

  const uploadRules = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = e.currentTarget;
    const tech = form.querySelector<HTMLInputElement>('input[name="technical"]');
    const med = form.querySelector<HTMLInputElement>('input[name="medical"]');
    const formData = new FormData();
    if (tech?.files?.[0]) formData.append('technical', tech.files[0]);
    if (med?.files?.[0]) formData.append('medical', med.files[0]);
    formData.append('name', 'default');
    formData.append('version', 'v1');
    await api.post('/rulesets/upload/', formData, { headers: { 'Content-Type': 'multipart/form-data' } });
    await fetchAudit();
  };

  const validate = async () => {
    await api.post('/validate/');
    await fetchResults();
  };

  function makeWaterfall(data: Record<string, number>) {
    const keys = Object.keys(data || {});
    const values = Object.values(data || {});
    const cumulative: number[] = [];
    let sum = 0;
    for (let i = 0; i < values.length; i++) {
      cumulative.push(sum);
      sum += values[i];
    }
    return {
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: keys },
      yAxis: { type: 'value' },
      series: [
        {
          name: 'assist',
          type: 'bar',
          stack: 'total',
          itemStyle: { borderColor: 'transparent', color: 'transparent' },
          emphasis: { itemStyle: { color: 'transparent' } },
          data: cumulative,
        },
        {
          name: 'value',
          type: 'bar',
          stack: 'total',
          label: { show: true, position: 'top' },
          data: values,
        },
      ],
    };
  }

  const countsOption = metrics ? makeWaterfall(metrics.counts_by_error) : { series: [] };
  const paidOption = metrics ? makeWaterfall(metrics.paid_by_error) : { series: [] };

  return (
    <div className="container">
      <div className="grid">
        <div className="card">
          <h2>Tenant: {tenant}</h2>
          <div style={{ display: 'flex', gap: 8 }}>
            <button onClick={validate}>Run Validation</button>
            <button onClick={fetchResults}>Refresh Results</button>
          </div>
        </div>

        <div className="card">
          <h3>Upload Claims</h3>
          <form onSubmit={uploadClaims}>
            <input type="file" name="claims" accept=".csv,.xlsx" />
            <button type="submit">Upload</button>
          </form>
        </div>

        <div className="card">
          <h3>Upload Rules</h3>
          <form onSubmit={uploadRules}>
            <input type="file" name="technical" />
            <input type="file" name="medical" />
            <button type="submit">Upload</button>
          </form>
        </div>

        <div className="card grid grid-2">
          <div>
            <h3>Claim Counts by Error</h3>
            <ReactEcharts option={countsOption} style={{ height: 300 }} />
          </div>
          <div>
            <h3>Paid Amount by Error</h3>
            <ReactEcharts option={paidOption} style={{ height: 300 }} />
          </div>
        </div>

        <div className="card">
          <h3>Audit</h3>
          <table className="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Type</th>
                <th>Status</th>
                <th>Created</th>
                <th>Finished</th>
              </tr>
            </thead>
            <tbody>
              {jobs.map((j) => (
                <tr key={j.id}>
                  <td>{j.id}</td>
                  <td>{j.job_type}</td>
                  <td>{j.status}</td>
                  <td>{j.created_at}</td>
                  <td>{j.finished_at || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="card">
          <h3>Results</h3>
          <table className="table">
            <thead>
              <tr>
                <th>Claim ID</th>
                <th>Status</th>
                <th>Error Type</th>
                <th>Explanation</th>
                <th>Recommended Action</th>
                <th>Paid (AED)</th>
              </tr>
            </thead>
            <tbody>
              {claims.map((c) => (
                <tr key={c.id}>
                  <td>{c.claim_id}</td>
                  <td>
                    <span className={`badge ${c.status === 'Validated' ? 'green' : 'red'}`}>{c.status}</span>
                  </td>
                  <td><span className="badge yellow">{c.error_type}</span></td>
                  <td style={{ whiteSpace: 'pre-wrap' }}>{c.error_explanation}</td>
                  <td style={{ whiteSpace: 'pre-wrap' }}>{c.recommended_action}</td>
                  <td>{c.paid_amount_aed}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
