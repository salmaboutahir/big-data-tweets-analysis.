
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import jade.core.AID;
import jade.core.Agent;
import jade.core.behaviours.TickerBehaviour;
import jade.lang.acl.ACLMessage;

import java.io.File;

public class AnalyzerAgent extends Agent {

    // Chemin vers le fichier state.json
    private static final String STATE_FILE =
            "C:\\Users\\hp\\Documents\\spark-mas-project\\jobs\\state.json";

    // Seuil de déséquilibre
    private static final double IMBALANCE_THRESHOLD = 5.0;

    // Pour éviter d'envoyer le même message en boucle
    private boolean previousImbalance = false;

    @Override
    protected void setup() {

        System.out.println("=================================");
        System.out.println("AnalyzerAgent démarré !");
        System.out.println("Surveillance continue du cluster...");
        System.out.println("Intervalle : 3 secondes");
        System.out.println("Seuil de déséquilibre : "
                + IMBALANCE_THRESHOLD + "%");
        System.out.println("=================================");

        /*
         * TickerBehaviour :
         * l'analyse est exécutée toutes les 3 secondes.
         */
        addBehaviour(new TickerBehaviour(this, 3000) {

            @Override
            protected void onTick() {

                analyserCluster();
            }
        });
    }

    /**
     * Analyse l'état actuel du cluster.
     */
    private void analyserCluster() {

        try {

            // ==============================
            // 1. Lecture de state.json
            // ==============================

            ObjectMapper mapper = new ObjectMapper();

            File file = new File(STATE_FILE);

            if (!file.exists()) {

                System.out.println(
                        "ERREUR : state.json introuvable !"
                );

                return;
            }

            JsonNode root = mapper.readTree(file);

            JsonNode workers = root.get("workers");

            if (workers == null) {

                System.out.println(
                        "ERREUR : section 'workers' absente dans state.json"
                );

                return;
            }

            // ==============================
            // 2. Lecture des charges CPU
            // ==============================

            double worker1 = workers
                    .get("spark-worker-1")
                    .get("cpu_percent")
                    .asDouble();

            double worker2 = workers
                    .get("spark-worker-2")
                    .get("cpu_percent")
                    .asDouble();

            double worker3 = workers
                    .get("spark-worker-3")
                    .get("cpu_percent")
                    .asDouble();

            // ==============================
            // 3. Affichage des charges
            // ==============================

            System.out.println();
            System.out.println("=================================");
            System.out.println("Analyse de la charge du cluster");
            System.out.println("=================================");

            System.out.println(
                    "Charge Worker 1 = "
                    + String.format("%.2f", worker1)
                    + "%"
            );

            System.out.println(
                    "Charge Worker 2 = "
                    + String.format("%.2f", worker2)
                    + "%"
            );

            System.out.println(
                    "Charge Worker 3 = "
                    + String.format("%.2f", worker3)
                    + "%"
            );

            // ==============================
            // 4. Calcul de la charge moyenne
            // ==============================

            double average =
                    (worker1 + worker2 + worker3) / 3.0;

            System.out.println(
                    "Charge moyenne = "
                    + String.format("%.2f", average)
                    + "%"
            );

            // ==============================
            // 5. Recherche du worker
            //    le plus chargé
            // ==============================

            double maxLoad = Math.max(
                    worker1,
                    Math.max(worker2, worker3)
            );

            // ==============================
            // 6. Recherche du worker
            //    le moins chargé
            // ==============================

            double minLoad = Math.min(
                    worker1,
                    Math.min(worker2, worker3)
            );

            // ==============================
            // 7. Identification du worker
            //    surchargé
            // ==============================

            String overloadedWorker;

            if (maxLoad == worker1) {

                overloadedWorker = "spark-worker-1";

            } else if (maxLoad == worker2) {

                overloadedWorker = "spark-worker-2";

            } else {

                overloadedWorker = "spark-worker-3";
            }

            // ==============================
            // 8. Identification du worker
            //    cible
            // ==============================

            String targetWorker;

            if (minLoad == worker1) {

                targetWorker = "spark-worker-1";

            } else if (minLoad == worker2) {

                targetWorker = "spark-worker-2";

            } else {

                targetWorker = "spark-worker-3";
            }

            // ==============================
            // 9. Calcul de la différence
            // ==============================

            double difference = maxLoad - minLoad;

            System.out.println(
                    "Différence max-min = "
                    + String.format("%.2f", difference)
                    + "%"
            );

            // ==============================
            // 10. Détection du déséquilibre
            // ==============================

            boolean currentImbalance =
                    difference > IMBALANCE_THRESHOLD;

            if (currentImbalance) {

                System.out.println(
                        "⚠️ DÉSÉQUILIBRE DÉTECTÉ !"
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
                        "Charge maximale : "
                        + String.format("%.2f", maxLoad)
                        + "%"
                );

                System.out.println(
                        "Charge minimale : "
                        + String.format("%.2f", minLoad)
                        + "%"
                );

                // ==============================
                // 11. Envoyer seulement un message
                //     lors de la détection
                // ==============================

                if (!previousImbalance) {

                    envoyerDecision(
                            overloadedWorker,
                            targetWorker,
                            maxLoad,
                            minLoad,
                            difference
                    );

                    previousImbalance = true;

                } else {

                    System.out.println(
                            "ℹ️ Déséquilibre toujours présent."
                    );

                    System.out.println(
                            "Aucun nouveau message envoyé."
                    );
                }

            } else {

                System.out.println(
                        "✅ Cluster équilibré."
                );

                System.out.println(
                        "Aucune intervention nécessaire."
                );

                // Réinitialiser l'état
                previousImbalance = false;
            }

            System.out.println(
                    "---------------------------------"
            );

        } catch (Exception e) {

            System.out.println(
                    "⚠️ Erreur pendant l'analyse du cluster."
            );

            System.out.println(
                    "Le prochain cycle réessaiera automatiquement."
            );

            e.printStackTrace();
        }
    }

    /**
     * Envoie une décision à DecisionAgent.
     */
    private void envoyerDecision(
            String overloadedWorker,
            String targetWorker,
            double maxLoad,
            double minLoad,
            double difference) {

        ACLMessage message =
                new ACLMessage(ACLMessage.INFORM);

        // Destinataire
        message.addReceiver(
                new AID(
                        "DecisionAgent",
                        AID.ISLOCALNAME
                )
        );

        // Contenu du message
        message.setContent(
                "DÉSÉQUILIBRE DÉTECTÉ"
                + " | OVERLOADED="
                + overloadedWorker
                + " | TARGET="
                + targetWorker
                + " | MAX_LOAD="
                + String.format("%.2f", maxLoad)
                + "%"
                + " | MIN_LOAD="
                + String.format("%.2f", minLoad)
                + "%"
                + " | DIFFERENCE="
                + String.format("%.2f", difference)
                + "%"
        );

        // Envoi
        send(message);

        System.out.println(
                "📩 Message envoyé à DecisionAgent."
        );

        System.out.println(
                "Contenu : "
                + message.getContent()
        );
    }

    /**
     * Méthode appelée lorsque l'agent est arrêté.
     */
    @Override
    protected void takeDown() {

        System.out.println(
                "AnalyzerAgent arrêté."
        );
    }
}

