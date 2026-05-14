import { Bot, ExternalLink, MessageSquare, Settings, Sparkles } from "lucide-react";
import { H2 } from "@nous-research/ui";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const portalItems = [
  {
    title: "Run Hermes",
    icon: Bot,
    body: "Start the local Hermes agent, connect Discord or another gateway, and use this console to monitor sessions and logs.",
  },
  {
    title: "Build Websites",
    icon: Sparkles,
    body: "Use the Agency Docs tab for the AI web agency workflow, including previews, review dashboards, WordPress, and Shopify packages.",
  },
  {
    title: "Review Conversations",
    icon: MessageSquare,
    body: "Open Sessions to inspect recent agent work, tool calls, and project decisions.",
  },
  {
    title: "Configure Services",
    icon: Settings,
    body: "Use Config and Keys to manage models, tool settings, Sitelet, Hermes proxy, and platform credentials.",
  },
];

export default function PortalPage() {
  return (
    <div className="space-y-5">
      <section className="border border-border bg-card/70 p-5 sm:p-6">
        <Badge variant="secondary">AI Solo Company Console</Badge>
        <H2 className="mt-3 text-2xl sm:text-3xl">Hermes Portal</H2>
        <p className="mt-3 max-w-3xl text-sm leading-6 text-muted-foreground normal-case">
          This console is the operating surface for Hermes: check runtime status,
          manage configuration, review sessions, inspect logs, schedule jobs, and
          open the AI web agency documentation.
        </p>
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {portalItems.map((item) => (
          <Card key={item.title}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <item.icon className="h-4 w-4" />
                {item.title}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm leading-6 text-muted-foreground normal-case">
                {item.body}
              </p>
            </CardContent>
          </Card>
        ))}
      </section>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ExternalLink className="h-4 w-4" />
            Common Next Actions
          </CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 text-sm text-muted-foreground normal-case md:grid-cols-3">
          <Action title="Check health" command="Open Status" />
          <Action title="Use website builder" command="Open Agency Docs" />
          <Action title="Debug gateway" command="Open Logs" />
        </CardContent>
      </Card>
    </div>
  );
}

function Action({ title, command }: { title: string; command: string }) {
  return (
    <div className="border border-border bg-background/30 p-3">
      <div className="mb-1 font-bold text-midground">{title}</div>
      <div className="font-mono-ui text-xs text-primary">{command}</div>
    </div>
  );
}
