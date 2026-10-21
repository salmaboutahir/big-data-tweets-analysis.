import jade.core.Profile;
import jade.core.ProfileImpl;
import jade.core.Runtime;
import jade.wrapper.AgentContainer;

public class Main {

    public static void main(String[] args) {

        try {

            Runtime runtime = Runtime.instance();

            Profile profile = new ProfileImpl();
            profile.setParameter(Profile.GUI, "true");

            AgentContainer container =
                    runtime.createMainContainer(profile);

            // Lancer DecisionAgent
            container.createNewAgent(
                    "DecisionAgent",
                    "DecisionAgent",
                    null
            ).start();

            // Lancer RebalancingAgent
            container.createNewAgent(
                    "RebalancingAgent",
                    "RebalancingAgent",
                    null
            ).start();

            // Lancer AnalyzerAgent
            container.createNewAgent(
                    "analyzer",
                    "AnalyzerAgent",
                    null
            ).start();

            System.out.println("JADE démarré avec succès !");

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}