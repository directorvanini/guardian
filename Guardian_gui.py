#!/usr/bin/env python3
"""
Guardian v2.0 - GUI Version
Professional interface for research fraud detection

Author: Kenneth Vanini
Organization: Sanctuary of Ma'at Research Institute
Date: February 16, 2026
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import os
import sys

# Import the core Guardian functions
from guardian_v2 import analyze_paper

class GuardianGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Guardian v2.0 - Research Fraud Detection System")
        self.root.geometry("1200x800")
        
        # Set color scheme
        self.bg_color = "#1a1a1a"
        self.fg_color = "#00ff00"
        self.text_bg = "#0d0d0d"
        self.button_color = "#2d2d2d"
        
        self.root.configure(bg=self.bg_color)
        
        self.create_widgets()
        
    def create_widgets(self):
        # ====================================================================
        # HEADER
        # ====================================================================
        header_frame = tk.Frame(self.root, bg=self.bg_color)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        title_label = tk.Label(
            header_frame,
            text="🛡️ GUARDIAN v2.0",
            font=("Courier New", 24, "bold"),
            bg=self.bg_color,
            fg=self.fg_color
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            header_frame,
            text="Research Fraud Detection System | Sanctuary of Ma'at Research Institute",
            font=("Courier New", 10),
            bg=self.bg_color,
            fg=self.fg_color
        )
        subtitle_label.pack()
        
        # ====================================================================
        # INPUT SECTION (TOP HALF)
        # ====================================================================
        input_frame = tk.LabelFrame(
            self.root,
            text="📄 INPUT",
            font=("Courier New", 12, "bold"),
            bg=self.bg_color,
            fg=self.fg_color,
            relief=tk.RIDGE,
            borderwidth=2
        )
        input_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Button row
        button_frame = tk.Frame(input_frame, bg=self.bg_color)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.upload_btn = tk.Button(
            button_frame,
            text="📁 Upload File",
            command=self.upload_file,
            font=("Courier New", 10, "bold"),
            bg=self.button_color,
            fg=self.fg_color,
            activebackground=self.fg_color,
            activeforeground=self.bg_color,
            relief=tk.RAISED,
            borderwidth=2,
            padx=20,
            pady=5
        )
        self.upload_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = tk.Button(
            button_frame,
            text="🗑️ Clear",
            command=self.clear_input,
            font=("Courier New", 10, "bold"),
            bg=self.button_color,
            fg=self.fg_color,
            activebackground=self.fg_color,
            activeforeground=self.bg_color,
            relief=tk.RAISED,
            borderwidth=2,
            padx=20,
            pady=5
        )
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        self.analyze_btn = tk.Button(
            button_frame,
            text="🔍 ANALYZE PAPER",
            command=self.analyze,
            font=("Courier New", 12, "bold"),
            bg="#003300",
            fg=self.fg_color,
            activebackground=self.fg_color,
            activeforeground=self.bg_color,
            relief=tk.RAISED,
            borderwidth=3,
            padx=30,
            pady=10
        )
        self.analyze_btn.pack(side=tk.RIGHT, padx=5)
        
        # Text input area
        input_label = tk.Label(
            input_frame,
            text="Paste paper text below or upload a file:",
            font=("Courier New", 9),
            bg=self.bg_color,
            fg=self.fg_color
        )
        input_label.pack(anchor=tk.W, padx=5, pady=(5, 0))
        
        self.input_text = scrolledtext.ScrolledText(
            input_frame,
            font=("Courier New", 9),
            bg=self.text_bg,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            relief=tk.SUNKEN,
            borderwidth=2,
            wrap=tk.WORD
        )
        self.input_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # ====================================================================
        # RESULTS SECTION (BOTTOM HALF)
        # ====================================================================
        results_frame = tk.LabelFrame(
            self.root,
            text="📊 RESULTS",
            font=("Courier New", 12, "bold"),
            bg=self.bg_color,
            fg=self.fg_color,
            relief=tk.RIDGE,
            borderwidth=2
        )
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Results text area
        self.results_text = scrolledtext.ScrolledText(
            results_frame,
            font=("Courier New", 9),
            bg=self.text_bg,
            fg=self.fg_color,
            relief=tk.SUNKEN,
            borderwidth=2,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # ====================================================================
        # STATUS BAR
        # ====================================================================
        status_frame = tk.Frame(self.root, bg=self.bg_color)
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.status_label = tk.Label(
            status_frame,
            text="Ready",
            font=("Courier New", 9),
            bg=self.bg_color,
            fg=self.fg_color,
            anchor=tk.W
        )
        self.status_label.pack(fill=tk.X)
        
    def upload_file(self):
        """Upload a file and load its contents"""
        filename = filedialog.askopenfilename(
            title="Select Paper File",
            filetypes=[
                ("Text Files", "*.txt"),
                ("Markdown Files", "*.md"),
                ("HTML Files", "*.html"),
                ("All Files", "*.*")
            ]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.input_text.delete(1.0, tk.END)
                self.input_text.insert(1.0, content)
                
                self.status_label.config(text=f"Loaded: {os.path.basename(filename)}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file:\n{str(e)}")
                self.status_label.config(text="Error loading file")
    
    def clear_input(self):
        """Clear the input field"""
        self.input_text.delete(1.0, tk.END)
        self.status_label.config(text="Input cleared")
    
    def analyze(self):
        """Analyze the paper text"""
        # Get input text
        paper_text = self.input_text.get(1.0, tk.END).strip()
        
        if not paper_text:
            messagebox.showwarning("No Input", "Please paste paper text or upload a file first!")
            return
        
        # Update status
        self.status_label.config(text="Analyzing paper...")
        self.root.update()
        
        try:
            # Run analysis
            report = analyze_paper(paper_text)
            
            # Format results
            results = self.format_results(report)
            
            # Display results
            self.results_text.config(state=tk.NORMAL)
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(1.0, results)
            self.results_text.config(state=tk.DISABLED)
            
            # Update status
            risk = report['overall_risk']
            if risk == 'CRITICAL':
                self.status_label.config(text="⛔ CRITICAL - Fraud patterns detected!")
            elif risk == 'FLAGGED':
                self.status_label.config(text="⚠️ FLAGGED - Some concerns detected")
            else:
                self.status_label.config(text="✅ PASS - No major issues detected")
                
        except Exception as e:
            messagebox.showerror("Analysis Error", f"Failed to analyze paper:\n{str(e)}")
            self.status_label.config(text="Analysis failed")
    
    def format_results(self, report):
        """Format the analysis report for display"""
        output = []
        
        # Header
        output.append("=" * 70)
        output.append("🚨 GUARDIAN v2.0 - RESEARCH FRAUD DETECTION REPORT")
        output.append("=" * 70)
        output.append("")
        
        # Overall Risk
        risk = report['overall_risk']
        if risk == 'CRITICAL':
            output.append("🚨 OVERALL RISK: CRITICAL")
        elif risk == 'FLAGGED':
            output.append("⚠️  OVERALL RISK: FLAGGED")
        else:
            output.append("✅ OVERALL RISK: PASS")
        
        output.append("=" * 70)
        output.append("")
        
        # Agent Statuses
        output.append("Risk Scores by Category:")
        for agent, status in report['agent_statuses'].items():
            if status == 'PASS':
                output.append(f"  ✅ {agent}: PASS")
            elif status == 'FLAGGED':
                output.append(f"  ⚠️  {agent}: FLAGGED")
            else:
                output.append(f"  🚨 {agent}: CRITICAL")
        
        output.append("")
        
        # Findings
        findings = report['all_findings']
        if findings:
            output.append(f"📋 FINDINGS ({len(findings)} total):")
            output.append("")
            
            for i, finding in enumerate(findings, 1):
                severity = finding['severity']
                symbol = '🚨' if severity == 'CRITICAL' else '⚠️'
                
                output.append(f"{i}. [{severity}] {symbol} {finding['issue']}")
                output.append(f"   Evidence: {finding['evidence']}")
                output.append(f"   Pattern: {finding['pattern']}")
                output.append("")
        else:
            output.append("✅ NO ISSUES DETECTED")
            output.append("")
        
        output.append("=" * 70)
        
        # Recommendation
        output.append("RECOMMENDATION:")
        output.append("=" * 70)
        
        if risk == 'CRITICAL':
            output.append("⛔ DO NOT PUBLISH - Exhibits patterns from major retracted papers")
        elif risk == 'FLAGGED':
            output.append("⚠️  REVIEW CAREFULLY - Some concerns detected, verify before publication")
        else:
            output.append("✅ APPEARS COMPLIANT - No major red flags detected")
        
        output.append("=" * 70)
        
        return "\n".join(output)


def main():
    """Main entry point for GUI"""
    # Check if guardian_v2 module is available
    try:
        import guardian_v2
    except ImportError:
        print("ERROR: guardian_v2.py not found!")
        print("Please ensure guardian_v2.py is in the same directory as this file.")
        input("Press Enter to exit...")
        sys.exit(1)
    
    root = tk.Tk()
    app = GuardianGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()