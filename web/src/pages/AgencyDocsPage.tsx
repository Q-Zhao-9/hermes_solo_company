import {
  BookOpen,
  CheckCircle2,
  Code2,
  Eye,
  FileText,
  GitBranch,
  Globe2,
  PackageOpen,
  PenTool,
  Rocket,
  Search,
  ShoppingBag,
  ShieldCheck,
  Workflow,
} from "lucide-react";
import { H2 } from "@nous-research/ui";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const phases = [
  {
    title: "1. Intake",
    icon: Search,
    body: "Collect the business type, target users, conversion goal, page list, platform preference, brand tone, and useful references.",
    command: "/create-site build a professional website for a local dental office",
  },
  {
    title: "2. Plan",
    icon: Workflow,
    body: "Create the brief, sitemap, design system, SEO/content plan, and platform route before writing code.",
    command: "brief -> sitemap -> design system -> content -> code",
  },
  {
    title: "3. Build",
    icon: Code2,
    body: "Use Codex to create or edit real project files in the selected site directory. Keep the work in source control.",
    command: "scripts/website_agency.py create-site --name \"Acme Dental\" --description \"Family dental clinic\" --pages home,about,services,contact",
  },
  {
    title: "4. Preview",
    icon: Eye,
    body: "Expose the local website through Hermes proxy first. Use Sitelet for static HTML fallback or WordPress previews.",
    command: "scripts/website_agency.py preview-share --project-dir generated-sites/acme-dental --prefer hermesproxy",
  },
  {
    title: "5. Review",
    icon: BookOpen,
    body: "Generate the client dashboard, collect approval or revision feedback, and keep the decision in project history.",
    command: "scripts/website_agency.py review-build --project-dir generated-sites/acme-dental --public-preview-url <preview-url>",
  },
  {
    title: "6. QA + Deploy",
    icon: Rocket,
    body: "Run QA, visual QA, then prepare or execute deployment only after the user approves production changes.",
    command: "scripts/website_agency.py qa --project-dir generated-sites/acme-dental",
  },
];

const platforms = [
  {
    name: "Static HTML",
    icon: FileText,
    use: "Landing pages, class demos, simple multi-page brochure websites.",
    command: "scripts/website_agency.py create-site --platform static --pages home,about,services,contact",
  },
  {
    name: "Next.js",
    icon: Globe2,
    use: "SaaS, AI product sites, dashboards, portals, auth, API routes, and custom apps.",
    command: "scripts/website_agency.py create-site --description \"SaaS dashboard with login\"",
  },
  {
    name: "WordPress",
    icon: PenTool,
    use: "Business-owner editable pages, content-heavy websites, blogs, and WordPress publishing workflows.",
    command: "scripts/website_agency.py wordpress-preview --project-dir <project> --spec dist/hermes-wordpress/home.json",
  },
  {
    name: "Shopify",
    icon: ShoppingBag,
    use: "Ecommerce storefronts, product pages, collection pages, and safe theme handoff packages.",
    command: "scripts/website_agency.py shopify-package --project-dir <project> --package-type product-page --title \"Product\" --handle product",
  },
];

const commands = [
  ["/create-site", "Create a complete website from business requirements."],
  ["/make-landing-page", "Create a one-page site."],
  ["/add-page", "Add about, service, product, contact, FAQ, pricing, or blog pages."],
  ["/edit-section", "Change one section by natural language."],
  ["/change-style", "Adjust color, typography, layout, or brand feeling."],
  ["/seo-optimize", "Improve titles, metadata, headings, schema, keywords, and internal links."],
  ["/build-preview", "Build and expose the current website preview."],
  ["/fix-build", "Use Codex to diagnose and fix build failures."],
  ["/deploy", "Prepare or run approved deployment."],
  ["/export", "Export HTML, WordPress package, Next.js repo, or Shopify theme package."],
];

const helpers = [
  "scripts/website_agency.py add-page --project-dir <project> --title FAQ --page-type faq",
  "scripts/website_agency.py media-plan --project-dir <project> --style \"bright clinical\"",
  "scripts/website_agency.py media-apply --project-dir <project>",
  "scripts/website_agency.py visual-qa --project-dir <project>",
  "scripts/website_agency.py approval-request --project-dir <project> --target deploy --reference deploy-static-dir",
  "scripts/website_agency.py approval-record --project-dir <project> --target deploy --reference deploy-static-dir --decision approved",
  "scripts/website_agency.py deploy-run --project-dir <project> --target static-dir --destination /srv/site --execute",
  "scripts/website_agency.py summary --project-dir <project>",
];

export default function AgencyDocsPage() {
  return (
    <div className="space-y-5">
      <section className="border border-border bg-card/70 p-5 sm:p-6">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div className="max-w-4xl space-y-3">
            <Badge variant="secondary">AI Solo Company</Badge>
            <H2 className="text-2xl sm:text-3xl">Web Agency Bot Guide</H2>
            <p className="max-w-3xl text-sm leading-6 text-muted-foreground normal-case">
              Use Hermes as a professional AI web agency: plan the business goal,
              generate the site, expose a preview, collect review feedback, run
              QA, then deploy or export only after approval.
            </p>
          </div>
          <div className="grid gap-2 text-xs text-muted-foreground normal-case sm:min-w-[260px]">
            <StatusLine label="Primary preview" value="Hermes proxy" />
            <StatusLine label="Fallback preview" value="Sitelet for static HTML" />
            <StatusLine label="Project history" value="docs/hermes-website-state.json" />
          </div>
        </div>
      </section>

      <section className="grid gap-4 xl:grid-cols-3">
        {phases.map((phase) => (
          <Card key={phase.title}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <phase.icon className="h-4 w-4" />
                {phase.title}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <p className="text-sm leading-6 text-muted-foreground normal-case">
                {phase.body}
              </p>
              <CodeBlock>{phase.command}</CodeBlock>
            </CardContent>
          </Card>
        ))}
      </section>

      <section className="grid gap-4 lg:grid-cols-[1fr_1fr]">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <PackageOpen className="h-4 w-4" />
              Platform Routing
            </CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3">
            {platforms.map((platform) => (
              <div key={platform.name} className="border border-border bg-background/30 p-3">
                <div className="mb-2 flex items-center gap-2 text-sm font-bold">
                  <platform.icon className="h-4 w-4" />
                  {platform.name}
                </div>
                <p className="mb-3 text-sm leading-6 text-muted-foreground normal-case">
                  {platform.use}
                </p>
                <CodeBlock>{platform.command}</CodeBlock>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <GitBranch className="h-4 w-4" />
              Bot Commands
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-2">
              {commands.map(([command, description]) => (
                <div
                  key={command}
                  className="grid gap-1 border-b border-border pb-2 last:border-b-0"
                >
                  <code className="font-mono-ui text-xs text-primary">{command}</code>
                  <span className="text-sm text-muted-foreground normal-case">
                    {description}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </section>

      <section className="grid gap-4 lg:grid-cols-[1fr_1fr]">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ShieldCheck className="h-4 w-4" />
              Approval Rules
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm leading-6 text-muted-foreground normal-case">
            <p>
              Always get explicit approval before production deployment,
              WordPress publishing, Shopify theme publishing, checkout-adjacent
              work, or any change that can affect billing, payment, tax, shipping,
              customer data, or live traffic.
            </p>
            <CodeBlock>
              scripts/website_agency.py review-comment --project-dir &lt;project&gt; --page home --decision revision_requested --comment "Client feedback"
            </CodeBlock>
            <CodeBlock>
              scripts/website_agency.py approval-record --project-dir &lt;project&gt; --target deploy --reference deploy-static-dir --decision approved
            </CodeBlock>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4" />
              Helper Reference
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {helpers.map((helper) => (
              <CodeBlock key={helper}>{helper}</CodeBlock>
            ))}
          </CardContent>
        </Card>
      </section>

      <Card>
        <CardHeader>
          <CardTitle>Recommended Student Workflow</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 text-sm leading-6 text-muted-foreground normal-case md:grid-cols-2">
          <ol className="list-decimal space-y-2 pl-5">
            <li>User describes the business and goal.</li>
            <li>Hermes creates brief, sitemap, design system, and content plan.</li>
            <li>Hermes generates the project with Codex and records state.</li>
            <li>Hermes shares a public preview with Hermes proxy.</li>
            <li>User requests revisions; Hermes edits files and reruns QA.</li>
          </ol>
          <ol className="list-decimal space-y-2 pl-5" start={6}>
            <li>Hermes builds the client review dashboard.</li>
            <li>Client approves or requests revision.</li>
            <li>Hermes prepares deployment, WordPress, or Shopify package.</li>
            <li>Production changes run only after approval.</li>
            <li>Hermes summarizes preview, QA, changed files, and next step.</li>
          </ol>
        </CardContent>
      </Card>
    </div>
  );
}

function StatusLine({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-4 border-b border-border pb-2 last:border-b-0">
      <span>{label}</span>
      <span className="font-mono-ui text-primary">{value}</span>
    </div>
  );
}

function CodeBlock({ children }: { children: string }) {
  return (
    <pre className="overflow-x-auto border border-border bg-black/35 p-3 text-xs leading-5 text-midground normal-case">
      <code>{children}</code>
    </pre>
  );
}
