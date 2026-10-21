import java.io.File;
import java.io.FileWriter;
import java.io.IOException;

import jade.core.Agent;
import jade.core.behaviours.CyclicBehaviour;
import jade.lang.acl.ACLMessage;

public class RebalancingAgent extends Agent {

    private static final String COMMAND_FILE =
            "C:\\Users\\hp\\Documents\\spark-mas-project\\jobs\\rebalance_command.json";

    @Override
    protected void setup() {

        System.out.println("=================================");
        System.out.println("RebalancingAgent démarré !");
        System.out.println("En attente des commandes...");
        System.out.println("=================================");

        addBehaviour(new CyclicBehaviour() {

            @Override
            public void action() {

                ACLMessage message = receive();

                if (message != null) {

                    System.out.println();
                    System.out.println("=================================");
                    System.out.println("📩 Commande reçue !");
                    System.out.println("=================================");

                    String content = message.getContent();

                    System.out.println(
                            "Expéditeur : "
                            + message.getSender().getLocalName()
                    );

                    System.out.println(
                            "Commande : " + content
                    );

                    if (content.contains("REBALANCING_REQUEST")) {

                        System.out.println(
                                "⚠️ Déséquilibre confirmé."
                        );

                        String overloadedWorker =
                                extraireValeur(
                                        content,
                                        "OVERLOADED="
                                );

                        String targetWorker =
                                extraireValeur(
                                        content,
                                        "TARGET="
                                );

                        System.out.println(
                                "Worker surchargé : "
                                + overloadedWorker
                        );

                        System.out.println(
                                "Worker cible : "
                                + targetWorker
                        );

                        System.out.println(
                                "🔄 Envoi de la commande à Spark..."
                        );

                        creerCommandeSpark(
                                overloadedWorker,
                                targetWorker
                        );

                    } else {

                        System.out.println(
                                "ℹ️ Commande inconnue."
                        );
                    }

                    System.out.println(
                            "================================="
                    );

                } else {

                    block();
                }
            }
        });
    }

    private void creerCommandeSpark(
            String overloadedWorker,
            String targetWorker) {

        try {

            File file = new File(COMMAND_FILE);

            FileWriter writer = new FileWriter(file);

            writer.write("{\n");
            writer.write("  \"action\": \"REPARTITION\",\n");
            writer.write("  \"overloaded_worker\": \""
                    + overloadedWorker + "\",\n");
            writer.write("  \"target_worker\": \""
                    + targetWorker + "\",\n");
            writer.write("  \"target_partitions\": 12\n");
            writer.write("}\n");

            writer.close();

            System.out.println(
                    "✅ Commande Spark créée avec succès."
            );

            System.out.println(
                    "📄 Fichier : " + COMMAND_FILE
            );

            System.out.println(
                    "🎯 Spark devra effectuer un repartitionnement."
            );

        } catch (IOException e) {

            System.out.println(
                    "❌ Erreur lors de la création de la commande Spark."
            );

            e.printStackTrace();
        }
    }

    private String extraireValeur(
            String content,
            String cle) {

        int debut = content.indexOf(cle);

        if (debut == -1) {
            return "UNKNOWN";
        }

        debut += cle.length();

        int fin = content.indexOf(" |", debut);

        if (fin == -1) {
            fin = content.length();
        }

        return content.substring(debut, fin).trim();
    }

    @Override
    protected void takeDown() {

        System.out.println(
                "RebalancingAgent arrêté."
        );
    }
}