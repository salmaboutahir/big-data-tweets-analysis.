import jade.core.AID;
import jade.core.Agent;
import jade.core.behaviours.CyclicBehaviour;
import jade.lang.acl.ACLMessage;

public class DecisionAgent extends Agent {

    @Override
    protected void setup() {

        System.out.println("=================================");
        System.out.println("DecisionAgent démarré !");
        System.out.println("En attente des messages...");
        System.out.println("=================================");

        addBehaviour(new CyclicBehaviour() {

            @Override
            public void action() {

                ACLMessage message = receive();

                if (message != null) {

                    String content = message.getContent();

                    System.out.println();
                    System.out.println("📩 Message reçu de : "
                            + message.getSender().getLocalName());

                    System.out.println("Contenu : " + content);

                    System.out.println(
                            "🤖 DecisionAgent analyse la situation..."
                    );

                    if (content.contains("DÉSÉQUILIBRE")) {

                        System.out.println(
                                "⚠️ Décision : intervention nécessaire !"
                        );

                        System.out.println(
                                "🔄 Envoi de la commande à RebalancingAgent..."
                        );

                        envoyerCommandeRebalancing(content);

                    } else {

                        System.out.println(
                                "✅ Décision : aucune intervention."
                        );
                    }

                } else {

                    block();
                }
            }
        });
    }

    /**
     * Envoie la commande au RebalancingAgent.
     */
    private void envoyerCommandeRebalancing(String content) {

        ACLMessage command =
                new ACLMessage(ACLMessage.REQUEST);

        // Destinataire
        command.addReceiver(
                new AID(
                        "RebalancingAgent",
                        AID.ISLOCALNAME
                )
        );

        // On transmet les informations reçues
        command.setContent(
                "REBALANCING_REQUEST | " + content
        );

        // Envoi
        send(command);

        System.out.println(
                "📤 Commande envoyée à RebalancingAgent."
        );

        System.out.println(
                "Commande : " + command.getContent()
        );
    }
}