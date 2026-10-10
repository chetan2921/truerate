// Static About content, condensed from .claude/plan/truerate/SPEC.md. Keep the two in step.

export const FLOW = [
  { title: "Paste a creator", detail: "Handle or profile link, optional product, quote and budget" },
  { title: "Read Instagram", detail: "Profile, last 30+ reels, 600 likers, newest followers, comments: about 20 HikerAPI requests" },
  { title: "Find ads, measure reels", detail: "Paid-partnership label, sponsor tags, #ad, then Gemini with cover images for the unclear ones" },
  { title: "Check the audience", detail: "Likes, followers and comments against WLDD creators of the same size" },
  { title: "Price", detail: "Ridge regression on WLDD's past deals (the 6 most similar shown for comparison), then sponsored-performance and fake-engagement adjustments" },
  { title: "Decide", detail: "Go, Negotiate or Avoid, with the reasons and negotiation lines" },
];

export const SIGNALS: [string, string, string][] = [
  ["Authenticity", "Fake-looking likers (account model on ~600 likers)", "Bought likes come from empty accounts. Like counts are cheap to fake; account quality is not"],
  ["Authenticity", "Fake-looking newest followers", "Bought followers arrive as a block of empty accounts, so the newest followers show a recent spike"],
  ["Authenticity", "Views per follower against similar creators", "Followers bought without reach show up as views far below the follower count"],
  ["Authenticity", "Likes per view against similar creators", "Seeded views have no real viewers behind them, so few of them turn into likes"],
  ["Authenticity", "Views and likes too even across reels", "Bot delivery is flat; real reach is spiky"],
  ["Authenticity", "Generic and repeated comment text (MiniLM)", "Bought and pod comments are emoji-only, templated and reused across reels"],
  ["Authenticity", "Accounts on 60% or more of reels; Louvain rings across WLDD creators", "Pods use real accounts, so only the coordination gives them away"],
  ["Authenticity", "Former usernames; IsolationForest on the whole pattern", "Renamed or bought pages, and fakes shaped in ways no single check predicts"],
  ["Engagement", "Likes and comments per view on own reels, percentile within the follower band", "Attention per view, comparable across account sizes"],
  ["Placement", "Paid reels' views against own reels, pulled toward the typical drop when there are few ads", "A brand buys sponsored performance, not organic peaks"],
  ["Placement", "Hidden-ad detection: rules, then Gemini on captions and covers, and Gemini listening to the 4 newest reels in a live analysis", "Many paid reels carry no #ad, and some ads are only said out loud ('use my code'); missing them corrupts the paid-vs-own comparison"],
  ["Placement", "Collab posts against own reels", "Shared-audience posts behave differently from both"],
  ["Placement", "Consistency over the last 10 reels and the trend", "Brands pay for the floor, and for where the creator is heading"],
  ["Audience", "Niche from WLDD's records, else the bio and captions", "Sets the category rate and the comparison group"],
  ["Audience", "Commenter mix and comment languages", "Shows whether people, creators, brands or bots engage, and which market they are in"],
  ["Audience", "Category value rank and product fit", "The same views are worth more in some categories, and off-topic ads underperform"],
];

export const FAKE_KINDS: Record<string, [string, string]> = {
  flat_views: ["Flat views", "Every reel set to the same views"],
  flat_views_noise: ["Flat views with noise", "Same views, plus or minus 10%"],
  bot_likers: ["Bot likers", "Half the likers replaced by bots, likes inflated to match"],
  pod_comments: ["Pod comments", "12 accounts leaving generic comments on 80% of reels"],
  bought_followers: ["Bought followers", "Followers tripled, 70% of the newest are bots"],
  smart_fake: ["Smart fake", "All of the above, mild, with specific-sounding comments"],
};

export const OTHER_PAGES: [string, string][] = [
  ["Faceless and meme pages", "Reach belongs to the page, so its delivery record replaces creator trust: typical weak-reel views, stability over 30 to 60 days, reach beyond followers. Price on expected views with a free repost if it under-delivers. Detect reposts by video and audio fingerprints, and pages run by one owner by cross-posting, shared links and overlapping commenters; count a cross-posted reel's views once."],
  ["UGC creators", "Split the fee three ways: production (rate card by format, scored against their portfolio), distribution (this model on their own reach, often near zero) and usage rights per month for running it as an ad. Ask for content-only and content-plus-post quotes; the gap is distribution."],
  ["Instagram IPs and series", "Value is retention: episode views against the page average, drop-off between episodes and returning commenters (here loyal fans, told apart from pods by account quality). Price per season with later episodes on the trend."],
  ["Across all of them", "Pricing on delivered views, account-quality sampling, comment checks, comparables plus regression and authenticity as a discount all carry over. What changes is the weight of creator trust and the unit priced. Check new prices by backtesting on WLDD's deals of that type, comparing predicted with delivered views after every campaign, and shadow-pricing next to human buyers."],
];

export const LIMITS = [
  "Follower spikes are a proxy: Instagram doesn't share follower history, so the check reads the newest followers. Real history builds from TrueRate's first snapshot.",
  "WLDD's 150 prices were agreed at different past dates, but only today's stats are visible. That noise sets a floor on accuracy.",
  "Hidden-ad detection is probabilistic. Reels it can't call stay out of the paid-vs-own comparison.",
  "The face check sees any face, so a fan page full of film stars passes. It only turns away clearly faceless pages.",
  "WLDD's own prices are noisy: two near-identical creators differ by a median 53%. No model or feature tried beat the current one beyond that noise.",
  "For creators bigger than any WLDD deal, the price is WLDD's extrapolation and the range stretches to published market asking prices, which WLDD usually pays below.",
];
