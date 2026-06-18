/**
 * Pre-configured certification data for CertCard compositions.
 * Each entry maps to a registered Remotion composition.
 */

export interface CertConfig {
  id: string;
  certName: string;
  certFullName: string;
  issuer: string;
  passDate: string;
  difficulty: string;
  factoids: [string, string, string];
  salaryImpact: string;
}

export const CERTS: CertConfig[] = [
  {
    id: "CertCard-CASP",
    certName: "CASP+",
    certFullName: "CompTIA Advanced Security Practitioner",
    issuer: "CompTIA",
    passDate: "2025",
    difficulty: "Advanced",
    factoids: [
      "< 25% pass rate",
      "DoD 8140 IAT Level III",
      "Highest CompTIA certification",
    ],
    salaryImpact: "+$15,200 avg salary boost",
  },
  {
    id: "CertCard-CCNA",
    certName: "CCNA",
    certFullName: "Cisco Certified Network Associate",
    issuer: "Cisco",
    passDate: "2025",
    difficulty: "Associate",
    factoids: [
      "Most recognized networking cert",
      "Required by 78% of network roles",
      "Cisco gateway certification",
    ],
    salaryImpact: "+$12,400 avg salary boost",
  },
  {
    id: "CertCard-AWS",
    certName: "AWS Security",
    certFullName: "AWS Certified Security - Specialty",
    issuer: "Amazon Web Services",
    passDate: "2025",
    difficulty: "Specialty",
    factoids: [
      "Cloud security gold standard",
      "Only 5% of AWS cert holders have it",
      "Top paying AWS certification",
    ],
    salaryImpact: "+$18,000 avg salary boost",
  },
  {
    id: "CertCard-SSCP",
    certName: "SSCP",
    certFullName: "Systems Security Certified Practitioner",
    issuer: "ISC\u00B2",
    passDate: "2025",
    difficulty: "Associate",
    factoids: [
      "ISC\u00B2 security credential",
      "Covers 7 security domains",
      "DoD 8140 IAT Level II",
    ],
    salaryImpact: "+$10,800 avg salary boost",
  },
  {
    id: "CertCard-SecurityPlus",
    certName: "Security+",
    certFullName: "CompTIA Security+",
    issuer: "CompTIA",
    passDate: "2025",
    difficulty: "Professional",
    factoids: [
      "#1 cybersecurity entry cert",
      "DoD 8140 IAT Level II",
      "890,000+ certified worldwide",
    ],
    salaryImpact: "+$9,400 avg salary boost",
  },
  {
    id: "CertCard-NetworkPlus",
    certName: "Network+",
    certFullName: "CompTIA Network+",
    issuer: "CompTIA",
    passDate: "2025",
    difficulty: "Professional",
    factoids: [
      "Vendor neutral networking",
      "Foundation for CCNA/CCNP",
      "Covers all network fundamentals",
    ],
    salaryImpact: "+$7,200 avg salary boost",
  },
  {
    id: "CertCard-CC",
    certName: "CC",
    certFullName: "Certified in Cybersecurity",
    issuer: "ISC\u00B2",
    passDate: "2025",
    difficulty: "Entry",
    factoids: [
      "ISC\u00B2 entry certification",
      "Cybersecurity fundamentals",
      "Gateway to CISSP track",
    ],
    salaryImpact: "+$5,600 avg salary boost",
  },
];
