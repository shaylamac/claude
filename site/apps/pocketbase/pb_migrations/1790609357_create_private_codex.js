/// <reference path="../pb_data/types.d.ts" />

migrate(
  (app) => {
    const users = app.findCollectionByNameOrId("users");
    users.createRule = null;
    users.deleteRule = null;
    app.save(users);

    const entries = new Collection({
      type: "base",
      name: "codex_entries",
      listRule: "@request.auth.id != ''",
      viewRule: "@request.auth.id != ''",
      createRule: null,
      updateRule: null,
      deleteRule: null,
      fields: [
        { name: "kind", type: "text", required: true, max: 30 },
        { name: "title", type: "text", required: true, max: 140 },
        { name: "category", type: "text", max: 80 },
        { name: "subtitle", type: "text", max: 160 },
        { name: "summary", type: "text", max: 1000 },
        { name: "body", type: "text", max: 5000 },
        { name: "note", type: "text", max: 500 },
        { name: "association", type: "text", max: 100 },
        { name: "position", type: "number", onlyInt: true },
        { name: "created", type: "autodate", onCreate: true, onUpdate: false },
        { name: "updated", type: "autodate", onCreate: true, onUpdate: true },
      ],
      indexes: ["CREATE INDEX idx_codex_kind_position ON codex_entries (kind, position)"],
    });
    app.save(entries);

    const rows = [
      ["character", "The First Marked", "Spiral Vampire", "The first to answer the call", "When the Spiral Mark appeared, the First Marked followed its pull toward the Kingdom instead of hiding it.", "A figure at the beginning of the Kingdom's newest chapter. Their identity remains closely guarded, but their choice to cross the threshold became a story whispered among the newly marked. Some call them a guide; others believe they are still searching for the reason the Moon Goddess chose them.", "Identity withheld in the surviving record.", "The Kingdom"],
      ["character", "The Night Archivist", "Spiral Vampire", "Keeper of unwritten histories", "A quiet custodian of the records that the Kingdom would rather forget.", "Beneath the Kingdom's public histories lies a second archive: fragments, testimonies, and names removed from the official account. The Night Archivist keeps it intact, convinced that every forgotten truth eventually returns to the surface.", "The archive has no public catalogue.", "The Archive"],
      ["character", "The Silver Sentinel", "Werewolf", "Guardian of the crossings", "A werewolf who watches the routes between the ordinary world and the Kingdom.", "The Silver Sentinel is known less by a name than by the promise they keep: no marked soul crosses alone if they can help it. Their knowledge of paths and borders makes them indispensable to travelers who do not yet understand the rules of the hidden world.", "Most sightings are recorded near moonrise.", "The Borderlands"],
      ["character", "The Threadkeeper", "Witch", "Reader of tangled possibilities", "A witch who studies the strange patterns that form around the Spiral Mark.", "Rather than foretell one fixed future, the Threadkeeper maps the many roads a marked person might take. They maintain that a divine mark opens a door; it does not decide what happens on the other side.", "Their diagrams often begin with a single spiral.", "The Moon Circle"],
      ["character", "The Gilded Envoy", "Fae", "An emissary between courts", "An elusive fae voice in matters that require patience, precision, and a careful choice of words.", "The Gilded Envoy carries messages between the Kingdom and the fae courts. Every promise in their presence is weighed with unusual care. Their loyalties remain a matter of debate, though their interest in the newly marked is unmistakable.", "A promise is never merely a promise.", "The Fae Courts"],
      ["character", "The Tidemother", "Mermaid", "Keeper of submerged memory", "A mermaid who remembers what the landbound Kingdom has let slip away.", "The Tidemother keeps stories in song beneath the waterline. Those who seek her counsel rarely receive a plain answer; instead, they return with an image or a melody that makes sense only when the tide changes.", "The sea remembers differently.", "The Deepwater Kin"],
      ["character", "The Star Witness", "Atrian", "Observer of the turning sky", "An Atrian drawn to the night the mark first appeared.", "The Star Witness records celestial changes and their echoes in the Kingdom. Of all the dates in their charts, June 3, 2019 remains the most heavily annotated. They believe the event was a beginning, not an isolated miracle.", "Several pages of their chart are missing.", "The Atrian Line"],
      ["character", "The Hollow Lantern", "Witch", "Guide through uncertain places", "A witch whose light is said to find paths where none seem to exist.", "The Hollow Lantern helps the newly marked navigate the first disorienting days after the Moon Goddess's call. Their methods are gentle but never simple: every lesson asks the traveler to decide what they are willing to carry into a new life.", "The lantern is lit only for those who ask.", "The Moon Circle"],
      ["family", "The Moon Circle", "Witch Lineage", "Readers of the old light", "A circle of witches who study the mark, its mysteries, and the choices it sets in motion.", "The Moon Circle is not bound by blood alone. Apprenticeship, shared duty, and a reverence for the Moon Goddess hold its members together. Their archives include early testimonies from the marked and diagrams that no two readers interpret quite the same way.", "Known for: patient study and careful counsel.", "Witches"],
      ["family", "The Deepwater Kin", "Mermaid Lineage", "Where memory follows the tide", "An ocean-bound lineage whose histories live in voices rather than books.", "The Deepwater Kin hold that a story changes with each telling but never wholly disappears. Their knowledge of the Kingdom predates many of its written accounts, and their meetings with the landbound are rare, deliberate, and seldom forgotten.", "Known for: song, memory, and hidden depths.", "Mermaids"],
      ["family", "The Atrian Line", "Atrian Lineage", "Witnesses to the heavens", "A lineage devoted to reading patterns in the sky and what they reveal below.", "The Atrian Line maintains charts that span generations. Its members are careful not to confuse observation with certainty; the night of the Spiral Mark has taught them how much can happen beyond even the clearest prediction.", "Known for: celestial records and long memory.", "Atrians"],
      ["family", "The Silver Pack", "Werewolf Lineage", "Bound by chosen loyalty", "A pack that guards passages at the edge of the Kingdom.", "The Silver Pack's strength lies as much in trust as in instinct. Some members were born into its traditions; others were taken in when the world changed beneath their feet. They know the crossings, the old paths, and the cost of keeping a border safe.", "Known for: guardianship and kinship.", "Werewolves"],
      ["family", "The Nocturne House", "Spiral Vampire Lineage", "A house beneath moonless windows", "A close-knit house of Spiral Vampires with a complicated place in the Kingdom's history.", "The Nocturne House preserves its own account of the Kingdom: one made of private debts, acts of protection, and names that official records omit. Its doors open rarely, but newly marked vampires have sometimes found refuge behind them.", "Known for: discretion and difficult loyalties.", "Spiral Vampires"],
      ["family", "The Gilded Court", "Fae Lineage", "An inheritance of promises", "A fae court whose alliances are written in ceremony and remembered for centuries.", "In the Gilded Court, words are an art and obligations an inheritance. Its emissaries negotiate with the Kingdom when the interests of the hidden peoples overlap. Outsiders are advised to listen carefully, and to promise only what they truly mean.", "Known for: diplomacy and binding words.", "Fae"],
      ["lore", "The Spiral Mark", "Origins", "A sign written on the left wrist", "A small spiral placed by the Moon Goddess on June 3, 2019. For the chosen, it is the first sign that an ordinary life is about to change.", "The mark appears on the left wrist. Small enough to be overlooked by a stranger, it carries an immense meaning to those who recognize it. It sets its bearer on a supernatural path and ties them to the hidden community known as the Kingdom. Whether it is a gift, a summons, or a test is still debated.", "First recorded: June 3, 2019.", "The Moon Goddess"],
      ["lore", "The Moon Goddess", "Origins", "The hand behind the mark", "The divine presence credited with placing the Spiral Mark and choosing those who bear it.", "For some, the Moon Goddess is a protective guide; for others, a distant power whose intentions cannot be known. Every marked person shares a connection to her act on June 3, 2019, though no two understand that connection in quite the same way.", "Her reasons remain a living question.", "The Spiral Mark"],
      ["lore", "The Kingdom", "Places", "The world behind the world", "A hidden community bound together by supernatural lives, old histories, and the arrival of the marked.", "The Kingdom is less a single place than a network of belonging, obligation, and guarded knowledge. Its people include Spiral Vampires, werewolves, witches, fae, mermaids, and Atrians. To the newly marked, finding it means discovering that the world was never as small as it seemed.", "Not every path into the Kingdom is visible.", "The Hidden World"],
      ["lore", "The Night of June Third", "Chronology", "The day the world quietly turned", "On June 3, 2019, the Moon Goddess placed the Spiral Mark on chosen people.", "There was no proclamation to the ordinary world. A small spiral appeared on left wrists, and lives began to move toward a hidden community. The Kingdom remembers the date as a threshold: a dividing line between the world before the mark and everything that followed.", "June 3, 2019 · The first marking.", "The Spiral Mark"],
      ["lore", "Spiral Vampires", "The Peoples", "A path shaped by the mark", "Vampires whose stories are bound to the Spiral Mark and the Kingdom's changing future.", "The Spiral Vampires carry questions of identity, belonging, and transformation into the heart of the Kingdom. Their name invokes the mark, but their lives cannot be reduced to it. Some protect old ways; others believe the new chapter demands a new kind of courage.", "One mark; many possible paths.", "The Nocturne House"],
      ["lore", "The Old Crossings", "Places", "Routes that refuse a map", "The passages between the ordinary world and the Kingdom are known to those who watch the borders.", "Crossings may be hidden in familiar landscapes or revealed only at particular hours. The Silver Pack keeps watch over routes used by the newly marked, who often arrive with more questions than possessions.", "A crossing is a beginning, not an answer.", "The Silver Pack"],
      ["lore", "The Fae Promise", "Customs", "Words that outlive the speaker", "Among the fae, a promise is treated as a thing with weight and consequence.", "The Gilded Court's ceremonies are built around careful language. The Kingdom's other peoples have learned to take the same care when negotiating across its threshold. Intent matters; wording matters too.", "Speak only what you intend to keep.", "The Gilded Court"],
      ["lore", "The Submerged Archive", "Places", "History held beneath the surface", "The Deepwater Kin preserve memory through song where written records cannot reach.", "A visitor might hear one story and discover later that its details have shifted with the tide. The Deepwater Kin do not call this an error. To them, memory is alive: not fixed on a page, but held and carried onward.", "Some histories can only be heard.", "The Deepwater Kin"],
    ];

    for (let i = 0; i < rows.length; i++) {
      const [kind, title, category, subtitle, summary, body, note, association] = rows[i];
      const record = new Record(entries);
      record.load({ kind, title, category, subtitle, summary, body, note, association, position: i + 1 });
      app.save(record);
    }
  },
  (app) => {
    app.delete(app.findCollectionByNameOrId("codex_entries"));
    const users = app.findCollectionByNameOrId("users");
    users.createRule = "";
    users.deleteRule = "id = @request.auth.id";
    app.save(users);
  },
);
