#!/usr/bin/env python3
"""
Job Scraper GUI Controller
A GUI application to manage job scraping sources and configurations.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from typing import Dict, Any
import webbrowser
from datetime import datetime

# Try to import WebsiteAnalyzer with graceful fallback
try:
    from website_analyzer import WebsiteAnalyzer
    ANALYZER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Warning: WebsiteAnalyzer not available: {e}")
    print("   Auto-analysis features will be disabled")
    ANALYZER_AVAILABLE = False
    WebsiteAnalyzer = None

class JobScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Jobs Scraper - Source Controller")
        self.root.geometry("1000x700")
        
        # Load configuration
        self.config_file = "config.py"
        self.sources_data = self.load_sources_config()
        
        # Initialize website analyzer if available
        if ANALYZER_AVAILABLE:
            self.analyzer = WebsiteAnalyzer()
        else:
            self.analyzer = None
        
        # Create main interface
        self.create_widgets()
        self.refresh_sources_list()
        
    def load_sources_config(self):
        """Load job sources from config.py"""
        try:
            # Read the config file and extract JOB_SOURCES
            with open(self.config_file, 'r') as f:
                config_content = f.read()
            
            # Extract JOB_SOURCES dictionary from config.py
            import ast
            import re
            
            # Find JOB_SOURCES in the file
            match = re.search(r'JOB_SOURCES\s*=\s*({.*?})\s*(?=\n\w|\n#|\nif|\Z)', 
                            config_content, re.DOTALL)
            
            if match:
                sources_str = match.group(1)
                # Parse the dictionary
                sources_dict = ast.literal_eval(sources_str)
                return sources_dict
            else:
                messagebox.showerror("Error", "Could not find JOB_SOURCES in config.py")
                return {}
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load config: {str(e)}")
            return {}
    
    def save_sources_config(self):
        """Save job sources back to config.py"""
        try:
            # Read the current config file
            with open(self.config_file, 'r') as f:
                config_content = f.read()
            
            # Format the JOB_SOURCES dictionary
            sources_str = "JOB_SOURCES = " + self.format_sources_dict()
            
            # Replace the JOB_SOURCES section
            import re
            pattern = r'JOB_SOURCES\s*=\s*{.*?}(?=\s*\n\w|\s*\n#|\s*\nif|\s*\Z)'
            new_content = re.sub(pattern, sources_str, config_content, flags=re.DOTALL)
            
            # Write back to file
            with open(self.config_file, 'w') as f:
                f.write(new_content)
                
            messagebox.showinfo("Success", "Configuration saved successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config: {str(e)}")
    
    def format_sources_dict(self):
        """Format sources dictionary for writing to config.py"""
        lines = ["{"]
        for key, value in self.sources_data.items():
            lines.append(f"    '{key}': {{")
            for sub_key, sub_value in value.items():
                if isinstance(sub_value, str):
                    lines.append(f"        '{sub_key}': '{sub_value}',")
                elif isinstance(sub_value, bool):
                    lines.append(f"        '{sub_key}': {sub_value},")
                elif isinstance(sub_value, list):
                    lines.append(f"        '{sub_key}': [")
                    for item in sub_value:
                        lines.append(f"            '{item}',")
                    lines.append("        ],")
                else:
                    lines.append(f"        '{sub_key}': {repr(sub_value)},")
            lines.append("    },")
        lines.append("}")
        return "\n".join(lines)
    
    def create_widgets(self):
        """Create the main GUI widgets"""
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Job Scraper Source Controller", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Left panel - Company list
        left_frame = ttk.LabelFrame(main_frame, text="Companies", padding="10")
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_frame.rowconfigure(0, weight=1)
        left_frame.columnconfigure(0, weight=1)
        
        # Companies treeview
        columns = ('Company', 'Status', 'Type')
        self.companies_tree = ttk.Treeview(left_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        self.companies_tree.heading('Company', text='Company')
        self.companies_tree.heading('Status', text='Status')
        self.companies_tree.heading('Type', text='Type')
        
        self.companies_tree.column('Company', width=150)
        self.companies_tree.column('Status', width=80)
        self.companies_tree.column('Type', width=80)
        
        # Scrollbar for treeview
        tree_scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.companies_tree.yview)
        self.companies_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        self.companies_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bind selection event
        self.companies_tree.bind('<<TreeviewSelect>>', self.on_company_select)
        
        # Right panel - Company details
        right_frame = ttk.LabelFrame(main_frame, text="Company Details", padding="10")
        right_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.columnconfigure(1, weight=1)
        
        # Company name
        ttk.Label(right_frame, text="Company Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.company_name_var = tk.StringVar()
        self.company_name_entry = ttk.Entry(right_frame, textvariable=self.company_name_var, width=40)
        self.company_name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Display name
        ttk.Label(right_frame, text="Display Name:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.display_name_var = tk.StringVar()
        self.display_name_entry = ttk.Entry(right_frame, textvariable=self.display_name_var, width=40)
        self.display_name_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # URL
        ttk.Label(right_frame, text="Career Page URL:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(right_frame, textvariable=self.url_var, width=40)
        self.url_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Test URL button
        self.test_url_btn = ttk.Button(right_frame, text="Test URL", command=self.test_url)
        self.test_url_btn.grid(row=2, column=2, pady=5, padx=(5, 0))
        
        # Test Analysis button (disabled if analyzer not available)
        self.test_analysis_btn = ttk.Button(right_frame, text="Test Analysis", command=self.test_analysis)
        self.test_analysis_btn.grid(row=2, column=3, pady=5, padx=(5, 0))
        if not ANALYZER_AVAILABLE:
            self.test_analysis_btn.config(state=tk.DISABLED)
        
        # Scraping type
        ttk.Label(right_frame, text="Scraping Type:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.type_var = tk.StringVar()
        
        # Include 'auto' only if analyzer is available
        if ANALYZER_AVAILABLE:
            type_values = ['auto', 'selenium', 'api', 'requests']
        else:
            type_values = ['selenium', 'api', 'requests']
            
        self.type_combo = ttk.Combobox(right_frame, textvariable=self.type_var, 
                                      values=type_values, width=37)
        self.type_combo.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Enabled checkbox
        self.enabled_var = tk.BooleanVar()
        self.enabled_check = ttk.Checkbutton(right_frame, text="Enable Scraping", 
                                           variable=self.enabled_var)
        self.enabled_check.grid(row=4, column=1, sticky=tk.W, pady=10, padx=(10, 0))
        
        # Search terms (for linkedin/indeed type sources)
        ttk.Label(right_frame, text="Search Terms:").grid(row=5, column=0, sticky=(tk.W, tk.N), pady=5)
        self.search_terms_text = tk.Text(right_frame, height=4, width=40)
        self.search_terms_text.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        search_scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.search_terms_text.yview)
        self.search_terms_text.configure(yscrollcommand=search_scrollbar.set)
        search_scrollbar.grid(row=5, column=2, sticky=(tk.N, tk.S), pady=5, padx=(5, 0))
        
        ttk.Label(right_frame, text="(One per line, for linkedin/indeed sources)", 
                 font=('Arial', 8)).grid(row=6, column=1, sticky=tk.W, padx=(10, 0))
        
        # Base URL (for linkedin/indeed type sources)
        ttk.Label(right_frame, text="Base URL:").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.base_url_var = tk.StringVar()
        self.base_url_entry = ttk.Entry(right_frame, textvariable=self.base_url_var, width=40)
        self.base_url_entry.grid(row=7, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Analysis Results
        ttk.Label(right_frame, text="Analysis Results:").grid(row=8, column=0, sticky=(tk.W, tk.N), pady=5)
        self.analysis_text = tk.Text(right_frame, height=4, width=40, state=tk.DISABLED)
        self.analysis_text.grid(row=8, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        analysis_scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.analysis_text.yview)
        self.analysis_text.configure(yscrollcommand=analysis_scrollbar.set)
        analysis_scrollbar.grid(row=8, column=2, sticky=(tk.N, tk.S), pady=5, padx=(5, 0))
        
        if ANALYZER_AVAILABLE:
            analysis_note = "(Auto-analysis when type is 'auto')"
        else:
            analysis_note = "(Analysis unavailable - install dependencies)"
        ttk.Label(right_frame, text=analysis_note, 
                 font=('Arial', 8)).grid(row=9, column=1, sticky=tk.W, padx=(10, 0))
        
        # Button frame
        button_frame = ttk.Frame(right_frame)
        button_frame.grid(row=10, column=0, columnspan=3, pady=20)
        
        # Buttons
        self.add_btn = ttk.Button(button_frame, text="Add New Company", command=self.add_company)
        self.add_btn.pack(side=tk.LEFT, padx=5)
        
        self.update_btn = ttk.Button(button_frame, text="Update Company", command=self.update_company)
        self.update_btn.pack(side=tk.LEFT, padx=5)
        
        self.delete_btn = ttk.Button(button_frame, text="Delete Company", command=self.delete_company)
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ttk.Button(button_frame, text="Clear Form", command=self.clear_form)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Bottom frame - Actions
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.grid(row=2, column=0, columnspan=2, pady=(20, 0), sticky=(tk.W, tk.E))
        
        self.save_btn = ttk.Button(bottom_frame, text="Save Configuration", 
                                  command=self.save_sources_config, style='Accent.TButton')
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        self.reload_btn = ttk.Button(bottom_frame, text="Reload Configuration", 
                                    command=self.reload_config)
        self.reload_btn.pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_var = tk.StringVar()
        self.status_var.set(f"Loaded {len(self.sources_data)} companies from config")
        self.status_label = ttk.Label(bottom_frame, textvariable=self.status_var)
        self.status_label.pack(side=tk.RIGHT)
    
    def refresh_sources_list(self):
        """Refresh the companies list"""
        # Clear existing items
        for item in self.companies_tree.get_children():
            self.companies_tree.delete(item)
        
        # Add companies
        for key, source in self.sources_data.items():
            name = source.get('name', key.title())
            status = "Enabled" if source.get('enabled', False) else "Disabled"
            source_type = source.get('type', 'selenium')
            
            self.companies_tree.insert('', 'end', iid=key, values=(name, status, source_type))
    
    def on_company_select(self, event):
        """Handle company selection"""
        selection = self.companies_tree.selection()
        if not selection:
            return
        
        company_key = selection[0]
        source = self.sources_data.get(company_key, {})
        
        # Fill form with selected company data
        self.company_name_var.set(company_key)
        self.display_name_var.set(source.get('name', ''))
        self.url_var.set(source.get('url', ''))
        self.type_var.set(source.get('type', 'auto' if ANALYZER_AVAILABLE else 'selenium'))
        self.enabled_var.set(source.get('enabled', False))
        self.base_url_var.set(source.get('base_url', ''))
        
        # Fill search terms
        search_terms = source.get('search_terms', [])
        self.search_terms_text.delete('1.0', tk.END)
        if search_terms:
            self.search_terms_text.insert('1.0', '\n'.join(search_terms))
    
    def clear_form(self):
        """Clear the form"""
        self.company_name_var.set('')
        self.display_name_var.set('')
        self.url_var.set('')
        self.type_var.set('auto' if ANALYZER_AVAILABLE else 'selenium')
        self.enabled_var.set(False)
        self.base_url_var.set('')
        self.search_terms_text.delete('1.0', tk.END)
        
        # Clear analysis results
        self.analysis_text.config(state=tk.NORMAL)
        self.analysis_text.delete('1.0', tk.END)
        self.analysis_text.config(state=tk.DISABLED)
        
        # Clear selection
        self.companies_tree.selection_remove(self.companies_tree.selection())
    
    def add_company(self):
        """Add a new company"""
        company_key = self.company_name_var.get().strip().lower().replace(' ', '_')
        display_name = self.display_name_var.get().strip()
        url = self.url_var.get().strip()
        
        if not company_key or not display_name:
            messagebox.showerror("Error", "Company name and display name are required")
            return
        
        if company_key in self.sources_data:
            messagebox.showerror("Error", "Company already exists")
            return
        
        # Create new source entry
        new_source = {
            'name': display_name,
            'enabled': self.enabled_var.get(),
            'type': self.type_var.get() or ('auto' if ANALYZER_AVAILABLE else 'selenium')
        }
        
        if url:
            new_source['url'] = url
            
        base_url = self.base_url_var.get().strip()
        if base_url:
            new_source['base_url'] = base_url
        
        # Add search terms if provided
        search_terms_text = self.search_terms_text.get('1.0', tk.END).strip()
        if search_terms_text:
            search_terms = [term.strip() for term in search_terms_text.split('\n') if term.strip()]
            if search_terms:
                new_source['search_terms'] = search_terms
        
        # Add to sources data
        self.sources_data[company_key] = new_source
        
        # Refresh list
        self.refresh_sources_list()
        
        # Select the new item
        self.companies_tree.selection_set(company_key)
        
        self.status_var.set(f"Added company: {display_name}")
    
    def update_company(self):
        """Update selected company"""
        selection = self.companies_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a company to update")
            return
        
        company_key = selection[0]
        display_name = self.display_name_var.get().strip()
        url = self.url_var.get().strip()
        
        if not display_name:
            messagebox.showerror("Error", "Display name is required")
            return
        
        # Update source entry
        source = self.sources_data[company_key]
        source['name'] = display_name
        source['enabled'] = self.enabled_var.get()
        source['type'] = self.type_var.get() or ('auto' if ANALYZER_AVAILABLE else 'selenium')
        
        if url:
            source['url'] = url
        elif 'url' in source:
            del source['url']
            
        base_url = self.base_url_var.get().strip()
        if base_url:
            source['base_url'] = base_url
        elif 'base_url' in source:
            del source['base_url']
        
        # Update search terms
        search_terms_text = self.search_terms_text.get('1.0', tk.END).strip()
        if search_terms_text:
            search_terms = [term.strip() for term in search_terms_text.split('\n') if term.strip()]
            if search_terms:
                source['search_terms'] = search_terms
            else:
                source.pop('search_terms', None)
        else:
            source.pop('search_terms', None)
        
        # Refresh list
        self.refresh_sources_list()
        
        # Re-select the updated item
        self.companies_tree.selection_set(company_key)
        
        self.status_var.set(f"Updated company: {display_name}")
    
    def delete_company(self):
        """Delete selected company"""
        selection = self.companies_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a company to delete")
            return
        
        company_key = selection[0]
        company_name = self.sources_data[company_key].get('name', company_key)
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {company_name}?"):
            del self.sources_data[company_key]
            self.refresh_sources_list()
            self.clear_form()
            self.status_var.set(f"Deleted company: {company_name}")
    
    def test_url(self):
        """Test the URL by opening it in browser"""
        url = self.url_var.get().strip()
        if url:
            try:
                webbrowser.open(url)
                self.status_var.set("URL opened in browser")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open URL: {str(e)}")
        else:
            messagebox.showerror("Error", "Please enter a URL to test")
    
    def test_analysis(self):
        """Test website analysis for the entered URL"""
        if not ANALYZER_AVAILABLE or self.analyzer is None:
            messagebox.showerror("Analysis Unavailable", 
                               "Website analysis is not available. Please install required dependencies:\n\n"
                               "pip install requests beautifulsoup4\n\n"
                               "Or run: ./setup_env.sh")
            return
            
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a URL to analyze")
            return
        
        # Show analyzing message
        self.analysis_text.config(state=tk.NORMAL)
        self.analysis_text.delete('1.0', tk.END)
        self.analysis_text.insert('1.0', "🔍 Analyzing website structure...")
        self.analysis_text.config(state=tk.DISABLED)
        self.root.update()
        
        try:
            # Perform analysis
            analysis = self.analyzer.analyze_website(url)
            
            # Format results
            strategy = analysis['recommended_strategy']
            confidence = analysis['confidence']
            explanation = self.analyzer.get_strategy_explanation(analysis)
            
            # Display detailed results
            results = f"Strategy: {strategy.upper()}\n"
            results += f"Confidence: {confidence:.1%}\n\n"
            results += f"Details:\n"
            results += f"• API detected: {'Yes' if analysis['api_detected'] else 'No'}\n"
            results += f"• JavaScript heavy: {'Yes' if analysis['javascript_heavy'] else 'No'}\n"
            results += f"• SPA detected: {'Yes' if analysis['spa_detected'] else 'No'}\n"
            results += f"• Anti-bot measures: {'Yes' if analysis['anti_bot_detected'] else 'No'}\n"
            results += f"• Response time: {analysis['response_time']:.2f}s\n\n"
            results += f"Explanation:\n{explanation}"
            
            # Update analysis text
            self.analysis_text.config(state=tk.NORMAL)
            self.analysis_text.delete('1.0', tk.END)
            self.analysis_text.insert('1.0', results)
            self.analysis_text.config(state=tk.DISABLED)
            
            # Auto-update type if it's currently 'auto'
            if self.type_var.get() == 'auto':
                self.type_var.set(strategy)
                
            self.status_var.set(f"Analysis completed - recommended: {strategy}")
            
        except Exception as e:
            error_msg = f"Analysis failed: {str(e)}"
            self.analysis_text.config(state=tk.NORMAL)
            self.analysis_text.delete('1.0', tk.END)
            self.analysis_text.insert('1.0', error_msg)
            self.analysis_text.config(state=tk.DISABLED)
            
            self.status_var.set("Analysis failed")
            messagebox.showerror("Analysis Error", error_msg)
    
    def reload_config(self):
        """Reload configuration from file"""
        if messagebox.askyesno("Confirm Reload", "This will discard any unsaved changes. Continue?"):
            self.sources_data = self.load_sources_config()
            self.refresh_sources_list()
            self.clear_form()
            self.status_var.set(f"Reloaded {len(self.sources_data)} companies from config")

def main():
    """Main entry point"""
    root = tk.Tk()
    app = JobScraperGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()