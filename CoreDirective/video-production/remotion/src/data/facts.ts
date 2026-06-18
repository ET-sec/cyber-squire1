/**
 * Pre-configured fact data for DidYouKnow compositions.
 * Each entry maps to a registered Remotion composition.
 */

export interface FactConfig {
  id: string;
  category: string;
  fact: string;
  source?: string;
  callToAction: string;
}

export const FACTS: FactConfig[] = [
  {
    id: "Fact-CyberJobs",
    category: "CAREER",
    fact: "Cybersecurity has 0% unemployment. There are 3.5 million unfilled positions globally.",
    source: "Cybersecurity Ventures 2025",
    callToAction: "Start your cyber career today",
  },
  {
    id: "Fact-Salary",
    category: "SALARY",
    fact: "Average cybersecurity salary in the US: $128,000. Top 10% earn over $200,000.",
    source: "BLS 2025",
    callToAction: "Follow for salary breakdowns",
  },
  {
    id: "Fact-Ransomware",
    category: "THREAT INTEL",
    fact: "A ransomware attack happens every 11 seconds. Average ransom payment: $1.5 million.",
    source: "Sophos Report",
    callToAction: "Learn to defend against this",
  },
  {
    id: "Fact-HumanError",
    category: "HACK",
    fact: "95% of cybersecurity breaches are caused by human error, not sophisticated hacking.",
    source: "IBM X-Force",
    callToAction: "Share this with your team",
  },
  {
    id: "Fact-NoDegree",
    category: "CAREER",
    fact: "You don't need a degree to work in cybersecurity. 25% of professionals have no bachelor's.",
    source: "ISC\u00B2 Workforce Study",
    callToAction: "Skills > Degrees. Follow for more.",
  },
  {
    id: "Fact-CASPSalary",
    category: "SALARY",
    fact: "CASP+ certification holders earn an average of $152,000 per year.",
    source: "CompTIA Salary Data",
    callToAction: "Get certified. Get paid.",
  },
  {
    id: "Fact-BreachCost",
    category: "THREAT INTEL",
    fact: "The average data breach costs $4.45 million. Healthcare breaches cost $10.9 million.",
    source: "IBM Cost of a Data Breach",
    callToAction: "This is why cyber pays well",
  },
  {
    id: "Fact-DoD8140",
    category: "CAREER",
    fact: "DoD 8140 requires specific certs for all military cyber roles. CASP+ qualifies for the highest level.",
    callToAction: "Military cyber? Follow for intel.",
  },
  {
    id: "Fact-FirstVirus",
    category: "HACK",
    fact: "The first computer virus (Creeper) was created in 1971. It just displayed: 'I'm the creeper, catch me if you can.'",
    callToAction: "Follow for more cyber history",
  },
  {
    id: "Fact-AWSCloud",
    category: "SALARY",
    fact: "Cybersecurity professionals with AWS Security Specialty earn 20% more than those without cloud certs.",
    source: "Global Knowledge",
    callToAction: "Cloud certs = more money",
  },
];
