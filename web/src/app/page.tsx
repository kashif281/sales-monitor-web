'use client';

import React, { useEffect, useState } from 'react';
import { Zap, Smartphone, ShoppingBag, Tag, RefreshCw, AlertCircle, Bell, X, Mail, ExternalLink, AlertTriangle, Briefcase, MessageSquare } from 'lucide-react';

interface SaleItem {
  "Brand Name": string;
  "Category": string;
  "Discount Percentage": string;
  "Source": string;
  "URL": string;
  // Merged fields
  "ImageURL"?: string;
  "FullTitle"?: string;
  "Rating"?: number;
  "Reviews"?: number;
  "Price"?: number;
  "OriginalPrice"?: number;
}

export default function Home() {
  const [data, setData] = useState<SaleItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [scraping, setScraping] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [isAlertModalOpen, setIsAlertModalOpen] = useState(false);
  const [alertForm, setAlertForm] = useState({ email: '', category: 'All', minDiscount: 20 });
  const [alertStatus, setAlertStatus] = useState<'idle' | 'submitting' | 'success' | 'error'>('idle');

  const handleAlertSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setAlertStatus('submitting');
    try {
      const res = await fetch('/api/alerts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(alertForm)
      });
      if (res.ok) {
        setAlertStatus('success');
        setTimeout(() => {
          setIsAlertModalOpen(false);
          setAlertStatus('idle');
          setAlertForm({ email: '', category: 'All', minDiscount: 20 });
        }, 2000);
      } else {
        setAlertStatus('error');
      }
    } catch (err) {
      setAlertStatus('error');
    }
  };

  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/sales');
      if (res.ok) {
        const json = await res.json();
        // Check if json is array
        if (Array.isArray(json)) {
          setData(json);
          setLastUpdated(new Date().toLocaleTimeString());
        }
      }
    } catch (error) {
      console.error("Failed to fetch data", error);
    } finally {
      setLoading(false);
    }
  };

  const handleScrape = async () => {
    setScraping(true);
    try {
      const res = await fetch('/api/scrape', { method: 'POST' });
      const result = await res.json();
      if (!result.success) {
        alert("Scraping failed: " + result.error);
      } else {
        // Refresh data after successful scrape
        await fetchData();
      }
    } catch (error) {
      alert("Failed to trigger scraper");
    } finally {
      setScraping(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <main className="min-h-screen bg-neutral-900 text-white p-8 font-sans">
      <div className="max-w-6xl mx-auto space-y-8">

        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-center bg-neutral-800 p-6 rounded-2xl border border-neutral-700 shadow-xl">
          <div className="space-y-2 text-center md:text-left">
            <h1 className="text-3xl font-bold bg-gradient-to-r from-teal-400 to-blue-500 bg-clip-text text-transparent">
              Retail Monitor Pakistan
            </h1>
            <p className="text-neutral-400 text-sm">
              Live discounts from top clothing & shoe brands
              {lastUpdated && <span className="ml-2 px-2 py-0.5 bg-neutral-700 rounded-full text-xs">Updated: {lastUpdated}</span>}
            </p>
          </div>

          <div className="flex items-center gap-4">
            <button
              onClick={() => {
                const partnerSection = document.getElementById('partner-section');
                partnerSection?.scrollIntoView({ behavior: 'smooth' });
              }}
              className="hidden lg:flex items-center gap-2 px-4 py-2 bg-neutral-900 border border-neutral-700 hover:border-neutral-500 text-neutral-300 rounded-lg transition-all text-sm font-medium"
            >
              <Briefcase className="w-4 h-4" />
              Partner with Us
            </button>
            <button
              onClick={() => setIsAlertModalOpen(true)}
              className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition-all text-sm font-medium shadow-lg shadow-indigo-600/20"
            >
              <Bell className="w-4 h-4" />
              Notify Me
            </button>
            <button
              onClick={handleScrape}
              disabled={scraping}
              className={`
                flex items-center gap-2 px-6 py-3 rounded-xl font-semibold transition-all
                ${scraping
                  ? 'bg-neutral-700 text-neutral-400 cursor-not-allowed'
                  : 'bg-teal-500 hover:bg-teal-400 text-neutral-900 hover:shadow-lg hover:shadow-teal-500/20 active:scale-95'}
              `}
            >
              <RefreshCw className={`w-5 h-5 ${scraping ? 'animate-spin' : ''}`} />
              {scraping ? 'Scanning Retailers...' : 'Scan for New Deals'}
            </button>
          </div>
        </div>

        {/* Category Filters */}
        <div className="flex flex-wrap gap-3 justify-center md:justify-start">
          {['All', 'Electronics', 'Mobile', 'Clothing', 'Shoes', 'Wireless Earbuds', 'Smart Watches'].map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`
                px-5 py-2 rounded-full text-sm font-semibold transition-all border
                ${selectedCategory === cat
                  ? 'bg-teal-500 text-neutral-900 border-teal-500 shadow-lg shadow-teal-500/20'
                  : 'bg-neutral-800 text-neutral-400 border-neutral-700 hover:border-neutral-500'}
              `}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Content */}
        {loading && data.length === 0 ? (
          <div className="text-center py-20 text-neutral-500 animate-pulse">Loading sales data...</div>
        ) : (
          <div className="space-y-12">

            {/* Real Data Section */}
            {data.filter(i => i.Source.includes('Real') && (selectedCategory === 'All' || i.Category?.trim() === selectedCategory)).length > 0 && (
              <section>
                <h2 className="text-2xl font-bold mb-6 flex items-center gap-2 text-green-400">
                  <span className="w-2 h-8 bg-green-500 rounded-full"></span>
                  Verified Live Sales {selectedCategory !== 'All' && <span className="text-neutral-500 text-sm font-normal">in {selectedCategory}</span>}
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {data
                    .filter(i => i.Source.includes('Real') && (selectedCategory === 'All' || i.Category?.trim() === selectedCategory))
                    .map((item, idx) => (
                      <BrandCard key={idx} item={item} />
                    ))}
                </div>
              </section>
            )}

            {/* Estimated/Frequent Data Section */}
            {data.filter(i => !i.Source.includes('Real') && (selectedCategory === 'All' || i.Category?.trim() === selectedCategory)).length > 0 && (
              <section>
                <h2 className="text-2xl font-bold mb-6 flex items-center gap-2 text-neutral-400">
                  <span className="w-2 h-8 bg-neutral-600 rounded-full"></span>
                  Frequent Sales & Estimates {selectedCategory !== 'All' && <span className="text-neutral-500 text-sm font-normal">in {selectedCategory}</span>}
                </h2>
                <p className="text-neutral-500 mb-6 -mt-4 text-sm">
                  These brands frequently have sales. Click "Visit Site" to check current offers manually.
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 opacity-90">
                  {data
                    .filter(i => !i.Source.includes('Real') && (selectedCategory === 'All' || i.Category?.trim() === selectedCategory))
                    .map((item, idx) => (
                      <BrandCard key={idx} item={item} />
                    ))}
                </div>
              </section>
            )}

          </div>
        )}

        {/* Partner with Us Section */}
        <div id="partner-section" className="mt-20 relative overflow-hidden rounded-3xl bg-indigo-600 p-8 md:p-12 shadow-2xl shadow-indigo-600/20">
          <div className="absolute top-0 right-0 -mt-20 -mr-20 w-64 h-64 bg-white/10 rounded-full blur-3xl"></div>
          <div className="absolute bottom-0 left-0 -mb-20 -ml-20 w-64 h-64 bg-indigo-900/30 rounded-full blur-3xl"></div>

          <div className="relative z-10 grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-6">
              <div className="inline-flex items-center gap-2 px-3 py-1 bg-white/20 backdrop-blur-md rounded-full text-xs font-bold uppercase tracking-wider text-white">
                <Briefcase className="w-3 h-3" />
                For Retailers
              </div>
              <h2 className="text-4xl font-extrabold text-white leading-tight">
                Get Your Brand in Front of Thousands of Shoppers
              </h2>
              <p className="text-indigo-100 text-lg">
                Are you a retailer in Pakistan? Partner with us to list your sales directly and boost your traffic during festive seasons.
              </p>
              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-start gap-3 bg-white/10 p-4 rounded-2xl backdrop-blur-sm border border-white/10">
                  <Zap className="w-5 h-5 text-yellow-300 shrink-0" />
                  <p className="text-sm font-medium text-white">Instant Visibility</p>
                </div>
                <div className="flex items-start gap-3 bg-white/10 p-4 rounded-2xl backdrop-blur-sm border border-white/10">
                  <Tag className="w-5 h-5 text-teal-300 shrink-0" />
                  <p className="text-sm font-medium text-white">Targeted Audience</p>
                </div>
              </div>
            </div>

            <div className="bg-neutral-900 rounded-2xl p-8 shadow-xl border border-white/10">
              <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <MessageSquare className="w-5 h-5 text-indigo-400" />
                Let's Collaborate
              </h3>
              <p className="text-neutral-400 text-sm mb-6">
                Send us an email with your brand details, and our team will get in touch to get your sales listed.
              </p>
              <a
                href="mailto:partnerships@retailmonitor.pk?subject=Partnership Inquiry - Retail Monitor Pakistan"
                className="block w-full text-center bg-white text-indigo-600 hover:bg-indigo-50 font-bold py-4 rounded-xl shadow-lg transition-all active:scale-95"
              >
                Email Partnerships Team
              </a>
              <p className="text-center text-xs text-neutral-500 mt-4">
                Typical response time: <span className="text-neutral-300 font-medium">24-48 hours</span>
              </p>
            </div>
          </div>
        </div>

        {!loading && data.length === 0 && (
          <div className="text-center py-20">
            <AlertTriangle className="w-12 h-12 text-yellow-500 mx-auto mb-4" />
            <h3 className="text-xl font-semibold mb-2">No Data Found</h3>
            <p className="text-neutral-400">Click "Scan for New Deals" to fetch the latest sales.</p>
          </div>
        )}
      </div>
      {/* Alert Subscription Modal */}
      {isAlertModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="relative w-full max-w-md bg-neutral-900 border border-neutral-800 rounded-2xl shadow-2xl p-6 overflow-hidden">
            <div className="absolute top-0 right-0 p-4">
              <button onClick={() => setIsAlertModalOpen(false)} className="text-neutral-500 hover:text-white transition-colors">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="mb-6">
              <div className="w-12 h-12 bg-indigo-600/20 rounded-xl flex items-center justify-center mb-4">
                <Bell className="w-6 h-6 text-indigo-500" />
              </div>
              <h2 className="text-2xl font-bold text-white mb-2">Price Drop Alerts</h2>
              <p className="text-neutral-400 text-sm">
                Never miss a deal again. We'll notify you as soon as prices drop for your favorite categories.
              </p>
            </div>

            {alertStatus === 'success' ? (
              <div className="py-8 text-center animate-in zoom-in duration-300">
                <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Zap className="w-8 h-8 text-green-500" />
                </div>
                <h3 className="text-xl font-bold text-white mb-2">You're Subscribed!</h3>
                <p className="text-neutral-400">We'll alert you to the best deals.</p>
              </div>
            ) : (
              <form onSubmit={handleAlertSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-neutral-400 mb-1.5">Email Address</label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-500" />
                    <input
                      type="email"
                      required
                      placeholder="alex@example.com"
                      value={alertForm.email}
                      onChange={(e) => setAlertForm({ ...alertForm, email: e.target.value })}
                      className="w-full bg-neutral-950 border border-neutral-800 rounded-xl py-2.5 pl-10 pr-4 text-white placeholder:text-neutral-600 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-neutral-400 mb-1.5">Category</label>
                    <select
                      value={alertForm.category}
                      onChange={(e) => setAlertForm({ ...alertForm, category: e.target.value })}
                      className="w-full bg-neutral-950 border border-neutral-800 rounded-xl py-2.5 px-4 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all"
                    >
                      {['All', 'Electronics', 'Mobile', 'Clothing', 'Shoes'].map(cat => (
                        <option key={cat} value={cat}>{cat}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-neutral-400 mb-1.5">Min. Discount</label>
                    <select
                      value={alertForm.minDiscount}
                      onChange={(e) => setAlertForm({ ...alertForm, minDiscount: parseInt(e.target.value) })}
                      className="w-full bg-neutral-950 border border-neutral-800 rounded-xl py-2.5 px-4 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all"
                    >
                      {[10, 20, 30, 40, 50, 70].map(d => (
                        <option key={d} value={d}>{d}% or more</option>
                      ))}
                    </select>
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={alertStatus === 'submitting'}
                  className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-bold py-3 rounded-xl shadow-lg shadow-indigo-600/20 transition-all mt-2"
                >
                  {alertStatus === 'submitting' ? 'Subscribing...' : 'Subscribe to Alerts'}
                </button>

                {alertStatus === 'error' && (
                  <p className="text-red-400 text-xs text-center">Something went wrong. Please try again.</p>
                )}
              </form>
            )}
          </div>
        </div>
      )}
    </main>
  );
}

function BrandCard({ item }: { item: SaleItem }) {
  // Use ImageURL if provided by scraper, otherwise use local placeholder
  const variant = (item["Brand Name"].length % 3) + 1;
  const placeholderPath = item.Category === 'Shoes'
    ? `/assets/shoes_${variant}.png`
    : (item.Category === 'Electronics' || item.Category === 'Mobile')
      ? `/assets/clothing_${variant}.png` // Generic for tech placeholders
      : `/assets/clothing_${variant}.png`;

  const imagePath = item.ImageURL || placeholderPath;

  return (
    <div className="group bg-neutral-800 border border-neutral-700 rounded-xl overflow-hidden hover:border-teal-500/50 transition-all hover:shadow-xl hover:-translate-y-1">
      {/* Image Header */}
      <div className="h-32 w-full relative overflow-hidden">
        <img
          src={imagePath}
          alt={item.Category}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-neutral-900 to-transparent opacity-90"></div>
        <div className="absolute bottom-2 left-4">
          <span className="text-xs px-2 py-1 bg-neutral-900/80 backdrop-blur-sm rounded-md text-neutral-300 flex items-center gap-1 border border-neutral-700">
            {item.Category === 'Clothing' ? <Tag className="w-3 h-3" /> : (item.Category === 'Mobile' ? <Smartphone className="w-3 h-3" /> : <ShoppingBag className="w-3 h-3" />)}
            {item.Category}
          </span>
        </div>
      </div>

      <div className="p-5 pt-3">
        <div className="flex justify-between items-start mb-4">
          <div className="space-y-1">
            <h3 className="font-bold text-lg text-neutral-200 line-clamp-2 leading-tight" title={item.FullTitle || item["Brand Name"]}>
              {item["Brand Name"]}
            </h3>
            <div className="flex flex-wrap gap-2 items-center">
              {item.Source.includes('Real') && (
                <span className="text-[10px] px-1.5 py-0.5 bg-green-900/30 text-green-400 rounded border border-green-900/50">
                  Verified Live
                </span>
              )}
              {item.Rating !== undefined && item.Rating > 0 && (
                <span className="text-[10px] px-1.5 py-0.5 bg-yellow-900/30 text-yellow-500 rounded border border-yellow-900/50 flex items-center gap-1">
                  ★ {item.Rating}
                </span>
              )}
            </div>
          </div>
          <div className="text-right">
            <span className="block text-3xl font-black text-teal-400 tracking-tighter">
              {item["Discount Percentage"]}
            </span>
            <span className="text-xs text-neutral-500 uppercase tracking-wider font-semibold">OFF</span>
          </div>
        </div>

        {item.Price && (
          <div className="mb-4 flex items-baseline gap-2">
            <span className="text-xl font-bold text-white">Rs. {item.Price.toLocaleString()}</span>
            <span className="text-sm text-neutral-500 line-through">Rs. {item.OriginalPrice?.toLocaleString()}</span>
          </div>
        )}

        <div className="pt-4 border-t border-neutral-700/50 flex justify-between items-center">
          <span className="text-xs text-neutral-500 font-mono line-clamp-1 w-2/3" title={item.Source}>
            Src: {item.Source}
          </span>
          <a
            href={item.URL}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-teal-500 hover:text-teal-400 font-medium flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap"
          >
            Visit Site <ExternalLink className="w-3 h-3" />
          </a>
        </div>
      </div>
    </div>
  );
}
