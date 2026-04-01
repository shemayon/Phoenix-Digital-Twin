'use client';

import { useEffect, useState } from 'react';
import { fetchTopology } from '@/lib/api';
import { motion } from 'framer-motion';
import { Cpu, Server, Database, ChevronRight, Share2 } from 'lucide-react';

interface TreeNode {
  name: string;
  type?: string;
  children?: TreeNode[];
}

function Node({ node, depth = 0 }: { node: TreeNode; depth?: number }) {
  const [isOpen, setIsOpen] = useState(true);
  const hasChildren = node.children && node.children.length > 0;

  return (
    <div className="ml-4">
      <div 
        className={`flex items-center gap-2 py-2 px-3 rounded-lg cursor-pointer transition-colors ${
          hasChildren ? 'hover:bg-slate-800/50' : 'hover:bg-teal-500/10'
        }`}
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="flex items-center gap-2">
            {depth === 0 ? <Server className="w-4 h-4 text-teal-400" /> : 
             hasChildren ? <Share2 className="w-4 h-4 text-violet-400" /> : 
             <Cpu className="w-4 h-4 text-slate-500" />}
            
            <span className={`text-xs font-bold uppercase tracking-widest ${
                depth === 0 ? 'text-white' : hasChildren ? 'text-slate-200' : 'text-slate-400'
            }`}>
                {node.name}
            </span>
            
            {node.type && (
                <span className="text-[9px] font-black text-slate-600 bg-slate-900 px-1.5 py-0.5 rounded border border-slate-800 ml-2">
                    {node.type.toUpperCase()}
                </span>
            )}
        </div>
        
        {hasChildren && (
            <ChevronRight className={`w-3.5 h-3.5 text-slate-600 transition-transform ${isOpen ? 'rotate-90' : ''}`} />
        )}
      </div>

      {isOpen && hasChildren && (
        <motion.div 
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="border-l border-slate-800 ml-2 mt-1"
        >
          {node.children!.map((child, idx) => (
            <Node key={`${child.name}-${idx}`} node={child} depth={depth + 1} />
          ))}
        </motion.div>
      )}
    </div>
  );
}

export default function TopologyView() {
  const [topology, setTopology] = useState<TreeNode | null>(null);

  useEffect(() => {
    fetchTopology().then(setTopology).catch(console.error);
  }, []);

  if (!topology) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teal-500"></div>
      </div>
    );
  }

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-3xl p-8 h-full overflow-hidden flex flex-col">
       <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <Cpu className="w-5 h-5 text-violet-400" />
            <h2 className="text-sm font-black text-slate-200 uppercase tracking-widest">UNS Infrastructure Topology</h2>
          </div>
          <div className="px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[9px] font-black uppercase tracking-widest">
            Nodes: Online
          </div>
       </div>

       <div className="flex-1 overflow-y-auto pr-4 custom-scrollbar">
          <Node node={topology} />
       </div>

       <div className="mt-8 pt-6 border-t border-slate-800/60">
          <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest leading-relaxed">
             Hierarchical mapping verified via IDSL/UNS Protocol v2.1. <br/>
             All edge compute nodes (PHX-DC-01/02) are broadcasting nominal telemetry.
          </p>
       </div>
    </div>
  );
}
