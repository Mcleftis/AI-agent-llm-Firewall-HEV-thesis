import argparse
import logging
import sys
import os
from AI_agent import train_ppo
from optimize import run_grid_search
from evaluate_agent import run_evaluation
from full_system import run_live_system


logging.basicConfig(
    level=logging.INFO, #emfanizontai INFO, WARNING, ERROR, CRITICAL
    format='%(asctime)s - %(levelname)s - %(message)s',#Wra, hmeromhnia, info, error, mhnyma pou grafoume emeis sto log
    handlers=[logging.StreamHandler(sys.stdout)]#Steile ta logs sthn othonh, sys.stdout na pane stohn konsola
)

def main():
    #emfanizetai an pathsoume python main.py --help
    parser = argparse.ArgumentParser(description="Neuro-Symbolic HEV Control System CLI")
    
    # Mode
    parser.add_argument(
        '--mode',#kaleitai me python main.py --mode train 
        type=str, 
        choices=['train', 'evaluate', 'demo', 'ablation', 'optimize'],#mono afta mporei na grapsei o xrhsths alliws varaei error
        required=True,#an den dwseis mode den trexei to programma
        help='Select operation mode: train (PPO), evaluate (Test), demo (Live), ablation (Study)'
    )

    parser.add_argument('--steps', type=int, default=100000, help='Total timesteps for PPO training')#posa timesteps tha ekpaideftei o PPO Agent,an den dwseis int tha exoume 100000
    parser.add_argument('--lr', type=float, default=0.0003, help='Learning rate for the optimizer')#omoiows me panw edw einai gia learning rate
    
    parser.add_argument('--traffic', type=str, default='normal', choices=['low', 'normal', 'heavy'], help='Traffic density simulation')# px mporoume an to kalesoume me python main.py --mode train --traffic heavy
    parser.add_argument('--driver_mood', type=str, default='neutral', help='Initial driver prompt (e.g., "I am in a hurry")')
    
    #edw leei pou tha apothikefsoume to arxeio
    parser.add_argument('--model_path', type=str, default='models/ppo_hev', help='Path to save/load the model')

    args = parser.parse_args()#afto diavazei ola ta arguments pou edwse o xrhsths sth consola

    
    logging.info(f"Starting System in [{args.mode.upper()}] mode")#ta kanoume k kefalaia na einai efdiakrita
    logging.info(f"Configuration: Traffic={args.traffic}, Mood='{args.driver_mood}'")

    try:
        if args.mode == 'train':
            logging.info("Starting PPO Training process...")
            train_ppo(steps=args.steps, lr=args.lr, save_path=args.model_path, traffic=args.traffic)
            logging.info(f"Training completed. Model saved at {args.model_path}")

        elif args.mode == 'evaluate':
            logging.info("Evaluating model performance...")
            results = run_evaluation(model_path=args.model_path, traffic=args.traffic)
            logging.info("Evaluation finished.")

        elif args.mode == 'demo':
            logging.info("Initializing Neuro-Symbolic Live Demo...")
            run_live_system(prompt=args.driver_mood, model_path=args.model_path)
            
        elif args.mode == 'ablation':
            logging.info("Running Ablation Study (No-LLM vs With-LLM)...")
            from run_ablation import run_study  # <--- Import το αρχείο που φτιάξαμε
            run_study()                         # <--- Εκτέλεση
        
        elif args.mode == 'optimize':
            logging.info("Starting Hyperparameter Optimization (Grid Search)...")
            from optimize import run_grid_search
            run_grid_search()
            
    except ImportError as e:#energopoieitai mono an exoume thema me ta imports
        logging.error(f"Could not import module: {e}")
        logging.error("Tip: Get assured that your files (train_agent.py etc.) are in the same folder.")
    except Exception as e:
        logging.error(f"Critical Error: {e}", exc_info=True)#h teleftai entolh deixnei olo to traceback. mas deixnei apeirws analytika ti kai pws.

if __name__ == "__main__":
    main()