import {
  Activity,
  Bot,
  BookOpen,
  Search,
  GitBranch,
  Layers,
  ChartNoAxesCombined,
  Database,
  ClipboardList,
  FileText,
  Settings,
} from "lucide-react";
export const navigation = [
  {
    label: "Overview",
    icon: Activity,
    group: "Workspace",
    title: "Operations overview",
    description:
      "Your investigations, review queue and measured results in one place.",
  },
  {
    label: "Agent workspace",
    icon: Bot,
    group: "Workspace",
    title: "Start an investigation",
    description:
      "Turn incident logs into a hypothesis supported by your runbooks.",
  },
  {
    label: "Incident analysis",
    icon: Search,
    group: "Workspace",
    title: "Incident analysis",
    description: "Find an investigation and follow the evidence behind it.",
  },
  {
    label: "RCA investigation",
    icon: GitBranch,
    group: "Workspace",
    title: "Investigation detail",
    description:
      "Review the hypothesis, supporting evidence and proposed recovery.",
  },
  {
    label: "Execution timeline",
    icon: Layers,
    group: "Workspace",
    title: "Execution timeline",
    description:
      "Follow the recorded steps, tool calls and verification attempts.",
  },
  {
    label: "Knowledge library",
    icon: BookOpen,
    group: "Intelligence",
    title: "Knowledge library",
    description:
      "Maintain the source documents that ground each investigation.",
  },
  {
    label: "Memory",
    icon: ClipboardList,
    group: "Intelligence",
    title: "Reviewed memory",
    description: "Revisit hypotheses retained after human review.",
  },
  {
    label: "Analytics & evaluations",
    icon: ChartNoAxesCombined,
    group: "Intelligence",
    title: "Analytics & evaluations",
    description:
      "Inspect measured outcomes, retrieval timing and case-level evidence.",
  },
  {
    label: "Reports & exports",
    icon: FileText,
    group: "Intelligence",
    title: "Reports & exports",
    description:
      "Take the investigation summary and evidence into your review process.",
  },
  {
    label: "Provider configuration",
    icon: Database,
    group: "Administration",
    title: "Providers & operations",
    description:
      "Inspect local services, optional integrations and operational measurements.",
  },
  {
    label: "Settings",
    icon: Settings,
    group: "Administration",
    title: "Workspace settings",
    description: "Manage this tab’s connection and your preferred appearance.",
  },
] as const;
